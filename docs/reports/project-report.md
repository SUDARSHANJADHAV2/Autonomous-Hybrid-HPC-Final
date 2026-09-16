# Unified project report

## Purpose

This repository unifies the supplied AI-Augmented HPC and HPC-Stack concepts into one platform. It is intentionally modular so the same control plane can operate a local Slurm cluster, a hybrid cluster with AWS burst workers, or a deterministic demonstration environment.

## Functional layers

1. Infrastructure as Code: Terraform manages persistent AWS networking and fixed resources.
2. Configuration management: Ansible configures Linux, time synchronization, Munge, identity, shared storage, Slurm, cgroups, monitoring, GPU workers, and cloud workers.
3. HPC scheduler: Slurm remains authoritative for node and job scheduling state; SlurmDBD/MariaDB stores accounting.
4. Observability: Prometheus is the telemetry source; Grafana renders dashboards; Node Exporter/DCGM/Slurm exporters feed it.
5. AIOps: detection, evidence collection, deterministic diagnosis, bounded optional AI, policy, action execution, verification, and audit.
6. Hybrid cloud: Boto3 launches/terminates ephemeral workers while Terraform continues to own persistent infrastructure.

## Design corrections made during unification

The original file-based state concept is not treated as authoritative. Independent agents do not directly mutate infrastructure. Cloud bursting is a real lifecycle, not a single launch call. AI is advisory, not a privileged shell. Monitoring is centralized. Configuration is parameterized rather than hard-coded to a fixed five-node topology.

## Validation boundary

The demo/test surface can be validated in this package without AWS or Slurm. Real deployment must be validated against the target Linux distribution, Slurm release, network topology, actual NVIDIA hardware, AWS account/quota, and site security policy.
