from ..models import CloudState

ALLOWED = {
    CloudState.REQUESTED: {CloudState.PROVISIONING},
    CloudState.PROVISIONING: {CloudState.BOOTING},
    CloudState.BOOTING: {CloudState.NETWORK_READY},
    CloudState.NETWORK_READY: {CloudState.CONFIGURING},
    CloudState.CONFIGURING: {CloudState.SLURM_REGISTERING},
    CloudState.SLURM_REGISTERING: {CloudState.AVAILABLE},
    CloudState.AVAILABLE: {CloudState.BUSY, CloudState.IDLE, CloudState.DRAINING},
    CloudState.BUSY: {CloudState.IDLE, CloudState.DRAINING},
    CloudState.IDLE: {CloudState.BUSY, CloudState.DRAINING},
    CloudState.DRAINING: {CloudState.TERMINATING},
    CloudState.TERMINATING: {CloudState.TERMINATED},
    CloudState.TERMINATED: set(),
}


def transition(current, target):
    current_state = CloudState(current)
    target_state = CloudState(target)
    if target_state not in ALLOWED[current_state]:
        raise ValueError(f"illegal cloud transition {current_state.value} -> {target_state.value}")
    return target_state
