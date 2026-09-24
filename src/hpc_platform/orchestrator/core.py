from __future__ import annotations

import uuid

from .actions import ActionExecutor
from ..diagnostics.rules import diagnose
from ..models import IncidentStatus


class Orchestrator:
    def __init__(self, db, policy, executor):
        self.db = db
        self.policy = policy
        self.executor = executor

    def handle(self, event):
        incident_id = "INC-" + uuid.uuid4().hex[:10].upper()
        self.db.incident(incident_id, event)
        self.db.set_status(incident_id, IncidentStatus.INVESTIGATING.value)
        diagnosis = diagnose(event)
        diagnosis.incident_id = incident_id
        self.db.save_diagnosis(diagnosis)
        self.db.set_status(incident_id, IncidentStatus.DIAGNOSED.value)
        decision = self.policy.decide(diagnosis, event.severity)
        if event.node:
            decision.parameters["node"] = event.node
        if event.job_id:
            decision.parameters["job_id"] = event.job_id
        if decision.requires_approval:
            self.db.set_status(incident_id, IncidentStatus.ACTION_REQUIRED.value)
            self.db.audit(
                incident_id, decision.action_type, "policy-engine", decision.reason, "PENDING_APPROVAL"
            )
            return {"incident_id": incident_id, "status": "AWAITING_APPROVAL", "action": decision.action_type}

        self.db.set_status(incident_id, IncidentStatus.REMEDIATING.value)
        result = self.executor.execute(incident_id, decision)
        final_status = IncidentStatus.VERIFIED if result["success"] else IncidentStatus.ESCALATED
        self.db.set_status(incident_id, final_status.value)
        return {
            "incident_id": incident_id,
            "status": final_status.value,
            "action": decision.action_type,
            "result": result,
        }
