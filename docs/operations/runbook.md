# Operator runbook

## Startup

Validate configuration, verify Chrony and Munge on all nodes, confirm `sinfo`, `squeue`, and `sacct`, then confirm Prometheus scrape targets. Start the control API only after those prerequisites are healthy.

## Node incident

Check `sinfo -R`, Slurm logs, exporter health, CPU/memory/disk/GPU telemetry, and recent job accounting. The control plane should create an incident before remediation. Drain actions must be followed by a Slurm-state verification.

## Cloud worker problem

Stop scheduling to the worker, inspect EC2 and network state, inspect cloud-worker logs, and reconcile AWS versus Slurm state. Never infer cloud health solely from a JSON cache.

## Recovery

For a controller outage, restore Slurm state/accounting according to site backup policy. Do not automatically recreate stateful controller services without validating `StateSaveLocation`, Munge identity, database availability, and node registrations.
