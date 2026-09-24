from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

class Severity(str, Enum):
    LOW="LOW"; MEDIUM="MEDIUM"; HIGH="HIGH"; CRITICAL="CRITICAL"
class AutomationMode(str, Enum):
    SAFE="SAFE"; ASSISTED="ASSISTED"; AUTONOMOUS="AUTONOMOUS"
class IncidentStatus(str, Enum):
    OPEN="OPEN"; INVESTIGATING="INVESTIGATING"; DIAGNOSED="DIAGNOSED"; ACTION_REQUIRED="ACTION_REQUIRED"; REMEDIATING="REMEDIATING"; VERIFIED="VERIFIED"; RESOLVED="RESOLVED"; ESCALATED="ESCALATED"
class CloudState(str, Enum):
    REQUESTED="REQUESTED"; PROVISIONING="PROVISIONING"; BOOTING="BOOTING"; NETWORK_READY="NETWORK_READY"; CONFIGURING="CONFIGURING"; SLURM_REGISTERING="SLURM_REGISTERING"; AVAILABLE="AVAILABLE"; BUSY="BUSY"; IDLE="IDLE"; DRAINING="DRAINING"; TERMINATING="TERMINATING"; TERMINATED="TERMINATED"
@dataclass
class Event:
    event_type: str
    source: str
    severity: Severity=Severity.MEDIUM
    node: str|None=None
    job_id: str|None=None
    payload: dict[str,Any]=field(default_factory=dict)
    event_id: str|None=None
    timestamp: str=field(default_factory=utcnow)
@dataclass
class Diagnosis:
    incident_id: str
    root_cause: str
    confidence: float
    evidence: list[str]=field(default_factory=list)
    recommended_action: str="NOOP"
    notes: str=""
@dataclass
class ActionDecision:
    action_type: str
    reason: str
    parameters: dict[str,Any]=field(default_factory=dict)
    requires_approval: bool=False
