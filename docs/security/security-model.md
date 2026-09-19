# Security model

No credentials are committed. AWS authentication should use an IAM role, workload identity or an operator-controlled AWS profile. SlurmDBD credentials are supplied through Ansible Vault. SSH uses keys, strict host verification and a bastion or site-approved private network.

The control API is read-only by default. Cloud mutations require both the hybrid mode and an explicit `HPC_ENABLE_CLOUD_MUTATIONS=1` gate; automation mode still applies policy approval semantics.

AI never receives an execution primitive. AI output is advisory data and cannot become a shell command. Slurm operations use a small, explicit allow-list and validate node/job identifiers before subprocess execution.

Prometheus and Grafana should remain on trusted/private networks. Docker workers are a lab/dev execution technique and must not be treated as equivalent to bare-metal production isolation without host-level cgroup/device/security validation.
