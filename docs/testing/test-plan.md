# Test Plan

## Unit/integration tests

Run `./scripts/validate.sh`. The suite covers cloud-state transition guards, SAFE/AUTONOMOUS policy behavior, orchestrator state recording, action failure handling, schema validity and deterministic demo execution.

## Infrastructure validation

Run Terraform formatting/validation in `infrastructure/terraform/environments/demo`, then run Ansible collection installation and `ansible-playbook --syntax-check infrastructure/ansible/playbooks/site.yml` before touching hosts.

## Functional HPC validation

On a disposable Linux cluster verify Chrony, Munge, LDAP identity, NFS mount, MariaDB/SlurmDBD, Slurm controller/compute registration, cgroup enforcement, CPU jobs, GPU GRES, Prometheus scraping, Grafana dashboards and Open OnDemand login workflows.

## Cloud lifecycle validation

Perform a dry-run first. Then verify the sequence `REQUESTED -> PROVISIONING -> BOOTING -> NETWORK_READY -> CONFIGURING -> SLURM_REGISTERING -> AVAILABLE`. Scale-down must drain, wait for Slurm completion, terminate EC2 and record `TERMINATED`.

## Automation safety

SAFE requires approval for mutating actions. ASSISTED also requires approval. AUTONOMOUS is limited to explicitly allow-listed operations; AI output remains advisory and cannot dispatch arbitrary shell commands.
