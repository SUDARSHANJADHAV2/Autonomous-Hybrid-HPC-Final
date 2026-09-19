# Failure scenarios

- OOM job: detector identifies OOM evidence; diagnosis proposes REQUEUE_JOB.
- Node down: incident opens; policy proposes DRAIN_NODE; verification checks Slurm state.
- GPU unhealthy: DCGM alert feeds a GPU incident and worker is removed from placement.
- Missing exporter: monitoring gap is recorded; no destructive action is taken.
- Cloud provisioning timeout: lifecycle does not advance to AVAILABLE; incident remains open and AWS resources are reconciled.
