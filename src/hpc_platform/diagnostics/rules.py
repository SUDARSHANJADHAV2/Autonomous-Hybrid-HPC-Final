from ..models import Diagnosis


def diagnose(event):
    payload = event.payload or {}
    event_type = event.event_type.upper()
    if event_type in {"NODE_UNHEALTHY", "NODE_DOWN"}:
        return Diagnosis("pending", "node health failure", 0.98, ["Slurm/telemetry reported node unhealthy"], "DRAIN_NODE", node_note(event))
    if event_type in {"QUEUE_PRESSURE", "PENDING_SPIKE"}:
        requested = max(1, min(int(payload.get("requested_nodes", 1)), 8))
        return Diagnosis("pending", "insufficient schedulable capacity", 0.95, ["pending queue pressure"], "SCALE_UP", f"requested_nodes={requested}")
    if event_type in {"JOB_OOM", "OOM"}:
        return Diagnosis("pending", "job exceeded memory limit", 0.99, ["OOM evidence"], "REQUEUE_JOB", "")
    if event_type in {"GPU_FAILURE", "GPU_UNHEALTHY"}:
        return Diagnosis("pending", "GPU telemetry/health failure", 0.93, ["GPU health evidence"], "DRAIN_NODE", node_note(event))
    if event_type == "MONITORING_GAP":
        return Diagnosis("pending", "telemetry exporter unavailable", 0.90, ["missing scrape target"], "NOTIFY", "")
    return Diagnosis("pending", "unknown operational condition", 0.40, ["no matching deterministic rule"], "NOTIFY", "")


def node_note(event):
    return f"node={event.node}" if event.node else ""
