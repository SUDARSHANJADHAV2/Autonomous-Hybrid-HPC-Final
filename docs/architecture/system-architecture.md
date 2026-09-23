# System architecture

The unified platform is deliberately split into four planes.

**HPC substrate:** Linux, Chrony, Munge, LDAP, NFS/LVM, Slurm, SlurmDBD/MariaDB, Cgroups v2, Open OnDemand, local Docker workers and GPU tooling.

**Observability:** Prometheus is the canonical time-series layer; Node Exporter covers host metrics, Slurm exporter covers scheduler/workload metrics, and DCGM Exporter covers NVIDIA GPU telemetry. Grafana is presentation only.

**Control plane:** detectors normalize events; diagnostics gather evidence; the deterministic policy engine decides; the orchestrator executes only allow-listed actions; verification confirms the expected post-condition; SQLite records incidents/actions/audit.

**Cloud plane:** Terraform owns persistent AWS networking and fixed infrastructure. Boto3 owns ephemeral burst workers. Tailscale, when selected by site policy, is a network transport rather than an authority or scheduler.

### Event pipeline

`Telemetry/Slurm/AWS -> Event -> Incident -> Evidence -> Diagnosis -> Policy -> Action -> Verification -> Audit`

### Ownership matrix

| State | Authority | Consumer |
|---|---|---|
| Node scheduling state | Slurm | detector/orchestrator |
| CPU/memory/GPU time series | Prometheus | health/diagnostics |
| EC2 state | AWS | cloud manager |
| Completed job accounting | SlurmDBD | diagnostics/reporting |
| Incident and action history | SQLite/Postgres-ready DB | API/UI/audit |
