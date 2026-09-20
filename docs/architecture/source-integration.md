# Source integration and provenance

## Project A

Source: `AI-Augmented-HPC-Management-Autonomous-Scaling-and-Intelligent-Diagnostics--for-Slurm-Cluster`.

Retained concepts: Ansible foundation; common/identity/storage/master/compute/login/portal roles; Chrony; Munge; LDAP integration; NFS with optional LVM; SlurmDBD/MariaDB; Cgroups v2; four operational agents; Gemini diagnostics; AWS/Tailscale cloud bursting; fault-injection mindset. The unified project keeps LDAP server provisioning and Open OnDemand packaging as explicit site/repository boundaries rather than pretending a generic Debian package task can safely encode every institutional identity and portal policy.

The original `group_vars/all.yml` contained a concrete LDAP/database password and a Tailscale auth-key placeholder. Those values are intentionally not copied into the unified project. Secrets now come from environment variables, Ansible Vault, AWS profiles/roles, or an external secret manager.

## Project B

Source: `HPC-Stack-A-Slurm-powered-Cloud-HPC-Solution-with-GPU-Support-on-Local-Machines.`

Retained concepts: AWS VPC/public-private subnet/IGW/NAT/bastion topology, hybrid Slurm design, Dockerized local workers, GPU/NVIDIA support, Prometheus/Grafana, Node Exporter/DCGM approach, and dependency intent for Docker/Terraform/Ansible/NVIDIA tooling.

The repository's tracked `controller.tf`, `compute.tf`, and `setup.yml` were one-byte placeholders in the inspected main branch. They are therefore replaced with working, parameterized implementations in this repository rather than copied unchanged.

## Combination rule

The unified codebase is a refactor, not a directory dump. Each original capability has one owner in the final architecture and duplicated authority is removed.
