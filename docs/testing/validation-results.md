# Validation Results

This document records the validation actually performed on the distributed archive.

## Automated checks completed

- Python bytecode compilation with `python -m compileall -q src tests`.
- Pytest suite.
- JSON Schema self-validation.
- YAML parsing for project configuration, Prometheus configuration and Ansible YAML files.
- Shell syntax checks with `bash -n` for all repository `.sh` files.
- Repository secret-pattern scan for common API keys, passwords and private keys.
- Archive manifest regeneration and checksum verification.

## Environment-dependent checks not executable in this build environment

- `terraform fmt` / `terraform validate` require the Terraform binary and AWS provider initialization.
- `ansible-playbook --syntax-check` requires Ansible and the `ansible.posix` collection.
- Real Slurm scheduling, Munge, NFS, LDAP, Open OnDemand, NVIDIA/DCGM, Tailscale and AWS execution require the target infrastructure.
- GPU behavior cannot be certified without a real NVIDIA host and matching driver/runtime.

The repository therefore distinguishes deterministic local validation from environment-dependent deployment validation. It does not claim zero-defect operation on arbitrary infrastructure.
