# Engineering Audit — 2026-09-10

## Findings fixed

1. Cloud lifecycle previously advanced through `NETWORK_READY`, `CONFIGURING`, and `SLURM_REGISTERING` without performing the corresponding checks. The lifecycle now requires an actual network provider, a successful Ansible configuration callback, and a positive Slurm readiness check. Failed bootstrap attempts perform best-effort EC2 cleanup and never record a non-schema `FAILED` cloud state.
2. `SCALE_UP` and `SCALE_DOWN` were previously simulation-only outside DEMO semantics. Real mode now wires Boto3, network verification, Ansible worker configuration, Slurm verification, and termination sequencing behind an explicit `HPC_ENABLE_CLOUD_MUTATIONS=1` gate.
3. Node/job context was not propagated from events into policy decisions. It is now copied into the action parameters, enabling DRAIN_NODE and REQUEUE_JOB to address the reported resource.
4. Slurm node drain was treated as successful when only the command returned. Real drain actions now wait for Slurm to report a drained/down node with no queued/running work.
5. The Dockerized Prometheus configuration used container-local `localhost`, which did not refer to the host exporters. Linux host-gateway addressing is now used.
6. GPU configuration was unconditional in the cloud worker playbook. GPU installation is now controlled by `gpu_enabled`, with the GRES configuration isolated to GPU hosts.
7. Munge was installed independently on hosts but its key was not synchronized. The common role now creates/reads the controller key and distributes the same key with restrictive permissions.
8. NFS storage configuration used a hard-coded AWS CIDR. The client CIDR is now a variable. An explicit `ansible.posix` collection dependency is declared.
9. SlurmDBD configuration was present but not deployed, and the service could start with a placeholder password. The configuration is now templated with mode 0600 and deployment fails early until an Ansible Vault-provided password is supplied.
10. Terraform previously created only networking/security groups despite documentation referring to a bastion/controller profile. Optional fixed bastion/controller resources are now represented in Terraform; ephemeral workers remain Boto3-owned.
11. The validator accidentally used repository-relative recursion assumptions. It now resolves the repository root explicitly and all scans are bounded to the repository.
12. The CLI and API previously implied generic success without clear mutation boundaries. Real cloud mutation is opt-in, while the HTTP surface remains read-only until authentication/authorization is deliberately configured.

## Validation status

The delivered archive was validated locally with 9 passing Python tests, Python compilation, YAML/JSON parsing, shell syntax checks and secret-pattern scanning. The environment does not contain Terraform or Ansible, so their executable validation is also encoded in CI but cannot honestly be reported as run locally. Real AWS, Slurm, LDAP, NFS, NVIDIA/DCGM, Tailscale and Open OnDemand integration remain environment-dependent acceptance tests.
