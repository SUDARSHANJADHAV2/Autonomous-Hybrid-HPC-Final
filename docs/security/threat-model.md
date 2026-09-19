# Threat model

Primary threats are credential leakage, remote execution through the AI layer, unauthorized Slurm control, exposed monitoring endpoints, compromised cloud-worker credentials, and state divergence between AWS and Slurm.

Mitigations: secret exclusion, IAM least privilege, allow-listed action types, schema-validated AI output, policy gating, audit logs, private networking, immutable infrastructure boundaries, verification after mutation, and explicit reconciliation of cloud/Slurm state.
