from __future__ import annotations

from ..models import ActionDecision


class ActionExecutor:
    def __init__(self, db, slurm=None, cloud_manager=None, dry_run=True, cloud_launch_defaults=None):
        self.db = db
        self.slurm = slurm
        self.cloud_manager = cloud_manager
        self.dry_run = dry_run
        self.cloud_launch_defaults = cloud_launch_defaults or {}

    def execute(self, incident_id, decision: ActionDecision):
        action_id = self.db.action(
            incident_id, decision.action_type, "orchestrator", decision.parameters, "RUNNING"
        )
        try:
            action = decision.action_type
            node = decision.parameters.get("node")
            if action == "DRAIN_NODE":
                if not node:
                    raise ValueError("DRAIN_NODE requires a node")
                if self.dry_run:
                    result = {"simulated": True, "node": node}
                else:
                    if self.slurm is None:
                        raise RuntimeError("Slurm client is not configured")
                    self.slurm.drain(node, "autonomous-hpc incident")
                    if not self.slurm.wait_node_drained(node, timeout=120):
                        raise RuntimeError(f"Slurm did not confirm node {node} drained")
                    result = {"verified": True, "node": node}
            elif action == "REQUEUE_JOB":
                job_id = decision.parameters.get("job_id")
                if not job_id:
                    raise ValueError("REQUEUE_JOB requires a job_id")
                result = {"simulated": True, "job_id": job_id} if self.dry_run else self.slurm.requeue(job_id)
            elif action == "SCALE_UP":
                if self.dry_run:
                    result = {"simulated": True, "requested_nodes": 1}
                else:
                    if self.cloud_manager is None:
                        raise RuntimeError("Cloud worker manager is not configured")
                    launch = {**self.cloud_launch_defaults, **decision.parameters.get("launch", {})}
                    node_name = node or decision.parameters.get("node_name") or self.cloud_manager.allocate_node_name()
                    result = self.cloud_manager.provision(node_name, launch).__dict__
            elif action == "SCALE_DOWN":
                if self.dry_run:
                    result = {"simulated": True, "requested_nodes": 1}
                else:
                    if self.cloud_manager is None:
                        raise RuntimeError("Cloud worker manager is not configured")
                    instance_id = decision.parameters.get("instance_id")
                    node_name = decision.parameters.get("node_name")
                    state = decision.parameters.get("state", "IDLE")
                    if not instance_id or not node_name:
                        candidates = [r for r in self.db.cloud_instances() if r["state"] == "IDLE"]
                        if not candidates:
                            raise RuntimeError("No IDLE cloud worker available for scale-down")
                        c = candidates[0]
                        instance_id, node_name, state = c["instance_id"], c["node_name"], c["state"]
                    result = self.cloud_manager.terminate(instance_id, node_name, state).__dict__
            elif action == "NOTIFY":
                result = {"simulated": self.dry_run, "action": action}
            else:
                raise ValueError(f"action not allow-listed: {action}")
            self.db.set_action_status(action_id, "SUCCEEDED")
            self.db.audit(incident_id, action, "orchestrator", decision.reason, "SUCCESS")
            return {"success": True, "action_id": action_id, "details": result}
        except Exception as exc:
            self.db.set_action_status(action_id, "FAILED")
            self.db.audit(incident_id, decision.action_type, "orchestrator", decision.reason, f"FAILURE:{exc}")
            return {"success": False, "action_id": action_id, "error": str(exc)}
