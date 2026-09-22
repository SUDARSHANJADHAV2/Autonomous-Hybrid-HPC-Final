from __future__ import annotations

import argparse
from pathlib import Path

from .cloud.aws import AWSCloud
from .cloud.manager import CloudWorkerManager
from .cloud.network import DirectSSHProvider, TailscaleProvider
from .config.settings import Settings
from .infrastructure import AnsibleConfigurator
from .models import Event, Severity
from .orchestrator.actions import ActionExecutor
from .orchestrator.core import Orchestrator
from .policy.engine import PolicyEngine
from .slurm.runner import SlurmClient
from .storage.db import DB


def build_orchestrator(settings):
    db = DB(settings.db_path)
    max_nodes = settings.get("cloud", "worker", "max_nodes", default=8)
    policy = PolicyEngine(settings.automation_mode, max_nodes)
    slurm = SlurmClient(enabled=settings.mode in {"local", "hybrid"})
    cloud_manager = None
    launch_defaults = {}

    mutations_enabled = settings.get("cloud", "mutations_enabled", default=False)
    import os
    mutations_enabled = mutations_enabled or os.getenv("HPC_ENABLE_CLOUD_MUTATIONS", "0") == "1"

    if settings.mode == "hybrid" and mutations_enabled:
        worker = settings.get("cloud", "worker", default={})
        launch_defaults = {
            "ami_id": worker.get("ami_id"),
            "instance_type": worker.get("instance_type_cpu", "t3.large"),
            "subnet_id": worker.get("subnet_id"),
            "security_group_id": worker.get("security_group_id"),
            "key_name": worker.get("ssh_key_name"),
        }
        network_name = settings.get("cloud", "networking", "provider", default="direct_ssh")
        network = TailscaleProvider() if network_name == "tailscale" else DirectSSHProvider()
        configurator = AnsibleConfigurator(Path.cwd())
        cloud = AWSCloud(settings.get("cloud", "region", default="us-east-1"), dry_run=False)
        configure = lambda node, target: configurator.configure(node, target, gpu_enabled=False)
        cloud_manager = CloudWorkerManager(cloud, db, network, configure, slurm, max_nodes)

    executor = ActionExecutor(
        db, slurm=slurm, cloud_manager=cloud_manager,
        dry_run=settings.mode == "demo" or cloud_manager is None,
        cloud_launch_defaults=launch_defaults,
    )
    return Orchestrator(db, policy, executor)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="hpcctl")
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("status", "nodes", "jobs", "incidents", "health"):
        sub.add_parser(name)
    diagnose_cmd = sub.add_parser("diagnose")
    diagnose_cmd.add_argument("event_type")
    diagnose_cmd.add_argument("--node")
    diagnose_cmd.add_argument("--job-id")
    demo = sub.add_parser("demo")
    demo.add_argument("--event", default="QUEUE_PRESSURE")
    for name in ("scale-up", "scale-down"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--dry-run", action="store_true")

    args = parser.parse_args(argv)
    settings = Settings()
    orchestrator = build_orchestrator(settings)
    db = orchestrator.db
    slurm = orchestrator.executor.slurm

    if args.cmd == "incidents":
        print(*db.incidents(), sep="\n")
        return 0
    if args.cmd in {"status", "health"}:
        print(f"mode={settings.mode} automation={settings.automation_mode} incidents={len(db.incidents())}")
        return 0
    if args.cmd == "nodes":
        print(slurm.nodes()["stdout"], end="")
        return 0
    if args.cmd == "jobs":
        print(slurm.jobs()["stdout"], end="")
        return 0
    if args.cmd == "diagnose":
        event = Event(args.event_type, "cli", Severity.HIGH, node=args.node, job_id=args.job_id)
        print(orchestrator.handle(event))
        return 0
    if args.cmd == "demo":
        print(orchestrator.handle(Event(args.event, "demo", Severity.HIGH, node="compute01")))
        return 0
    if args.cmd.startswith("scale-"):
        print(f"{'dry-run' if args.dry_run else 'policy-mediated'} {args.cmd}")
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
