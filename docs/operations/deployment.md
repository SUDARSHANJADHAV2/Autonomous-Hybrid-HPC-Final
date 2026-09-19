# Deployment guide

## Demo

Use the Python demo and tests; no AWS credentials, GPUs, or Slurm are required.

## Local

1. Install Ansible and the collections in `infrastructure/ansible/requirements.yml`.
2. Populate `inventory/local.ini` with real hosts.
3. Put the Slurm accounting password in Ansible Vault as `slurm_db_password`.
4. Run `ansible-playbook -i infrastructure/ansible/inventory/local.ini infrastructure/ansible/playbooks/site.yml`.
5. Verify Chrony, Munge, LDAP lookups, NFS, `slurmctld`, `slurmdbd`, `sinfo`, `squeue`, `sacct`, Node Exporter and any GPU exporter before starting the control API.

## Hybrid

1. Apply `infrastructure/terraform/environments/demo` for persistent AWS networking. The optional bastion/controller instances are also Terraform-owned.
2. Use a cloud AMI that already satisfies the site's SSH/Tailscale policy; the platform does not embed a secret Tailscale key into Terraform user-data.
3. Validate one manually configured worker with Ansible first.
4. Set `HPC_ENABLE_CLOUD_MUTATIONS=0` during dry-run/acceptance testing.
5. Only after Slurm registration, network reachability and Ansible idempotency are verified should `HPC_ENABLE_CLOUD_MUTATIONS=1` be considered. `HPC_AUTOMATION_MODE=AUTONOMOUS` is a separate operator decision and remains subject to the allow-listed action policy.

## Infrastructure ownership

Terraform owns long-lived VPC/subnets/routes/NAT/security groups and optional fixed hosts. Boto3 owns ephemeral burst workers. This boundary must not be violated by importing burst instances into Terraform state.
