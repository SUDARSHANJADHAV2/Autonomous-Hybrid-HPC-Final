from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .lifecycle import transition
from ..models import CloudState


@dataclass
class WorkerResult:
    instance_id: str
    node: str
    state: CloudState
    details: dict


class CloudWorkerManager:
    def __init__(self, cloud, db, network=None, configure: Callable[[str, str], dict] | None = None, slurm=None, max_nodes: int = 8):
        self.cloud = cloud
        self.db = db
        self.network = network
        self.configure = configure
        self.slurm = slurm
        self.max_nodes = max(1, int(max_nodes))

    def allocate_node_name(self) -> str:
        used = {r["node_name"] for r in self.db.cloud_instances() if r["state"] != CloudState.TERMINATED.value}
        for i in range(1, self.max_nodes + 1):
            name = f"cloud{i:02d}"
            if name not in used:
                return name
        raise RuntimeError(f"cloud worker capacity exhausted (max_nodes={self.max_nodes})")

    def _set(self, instance_id: str, node: str, current: CloudState, target: CloudState, details=None) -> CloudState:
        state = transition(current, target)
        self.db.record_cloud(instance_id, node, state.value, details or {})
        return state

    def provision(self, node: str, launch_kwargs: dict, timeout: int = 300) -> WorkerResult:
        launch = self.cloud.launch(**launch_kwargs, tags={"Name": node, "ManagedBy": "autonomous-hybrid-hpc"})
        instance_id = str(launch["instance_id"])
        state = CloudState.REQUESTED
        self.db.record_cloud(instance_id, node, state.value, launch)
        try:
            state = self._set(instance_id, node, state, CloudState.PROVISIONING)
            running = self.cloud.wait_running(instance_id, timeout=timeout)
            state = self._set(instance_id, node, state, CloudState.BOOTING, running)
            target = str(running.get("private_ip") or running.get("public_ip") or node)
            if self.network is None:
                raise RuntimeError("NetworkProvider is required for cloud-worker provisioning")
            network = self.network.connect(target)
            if not network.connected:
                raise RuntimeError(f"Network readiness failed for {target}: {network.detail}")
            state = self._set(instance_id, node, state, CloudState.NETWORK_READY, {"target": target, "network": network.detail})
            if self.configure is None:
                raise RuntimeError("worker configuration callback is required before activation")
            details = self.configure(node, target)
            if not details.get("success", False):
                raise RuntimeError(f"worker configuration failed: {details}")
            state = self._set(instance_id, node, state, CloudState.CONFIGURING, details)
            state = self._set(instance_id, node, state, CloudState.SLURM_REGISTERING)
            if self.slurm is None or not self.slurm.wait_node_ready(node, timeout=timeout):
                raise RuntimeError(f"Slurm did not report worker {node} ready")
            state = self._set(instance_id, node, state, CloudState.AVAILABLE)
            return WorkerResult(instance_id, node, state, {"running": running})
        except Exception as exc:
            try:
                self.cloud.terminate(instance_id)
                self.db.record_cloud(instance_id, node, CloudState.TERMINATED.value, {"failure": str(exc)})
            except Exception as cleanup_exc:
                self.db.record_cloud(instance_id, node, state.value, {"failure": str(exc), "cleanup_failure": str(cleanup_exc)})
            raise

    def terminate(self, instance_id: str, node: str, current_state, reason: str = "scale-down") -> WorkerResult:
        state = CloudState(current_state)
        if state in {CloudState.AVAILABLE, CloudState.BUSY, CloudState.IDLE}:
            if self.slurm is None:
                raise RuntimeError("Slurm client is required to drain a worker before termination")
            state = self._set(instance_id, node, state, CloudState.DRAINING, {"reason": reason})
            self.slurm.drain(node, reason)
        if state is CloudState.DRAINING:
            if self.slurm is None or not self.slurm.wait_node_drained(node, timeout=300):
                raise RuntimeError(f"worker {node} is not safe to terminate yet")
            state = self._set(instance_id, node, state, CloudState.TERMINATING, {"reason": reason})
        elif state is not CloudState.TERMINATING:
            state = self._set(instance_id, node, state, CloudState.TERMINATING, {"reason": reason})
        self.cloud.terminate(instance_id)
        state = self._set(instance_id, node, state, CloudState.TERMINATED, {"reason": reason})
        return WorkerResult(instance_id, node, state, {})
