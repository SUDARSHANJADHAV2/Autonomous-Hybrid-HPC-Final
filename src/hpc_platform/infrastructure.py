from __future__ import annotations

import os
import subprocess
from pathlib import Path


class AnsibleConfigurator:
    """Run only the repository's fixed worker playbook; never accept arbitrary shell text."""

    def __init__(self, project_root: str | Path):
        self.root = Path(project_root).resolve()
        self.playbook = self.root / "infrastructure/ansible/playbooks/provision_worker.yml"

    def configure(self, node: str, ansible_host: str, gpu_enabled: bool = False) -> dict:
        if not self.playbook.exists():
            raise FileNotFoundError(self.playbook)
        inventory = self.root / "data" / "runtime-cloud-inventory.ini"
        inventory.parent.mkdir(parents=True, exist_ok=True)
        line = f"{node} ansible_host={ansible_host}"
        user = os.getenv("HPC_ANSIBLE_USER")
        if user:
            line += f" ansible_user={user}"
        inventory.write_text(f"[cloud_workers]\n{line}\n", encoding="utf-8")
        command = [
            "ansible-playbook", "-i", str(inventory), str(self.playbook),
            "--limit", node, "-e", f"gpu_enabled={'true' if gpu_enabled else 'false'}",
        ]
        key = os.getenv("HPC_ANSIBLE_PRIVATE_KEY_FILE")
        if key:
            command.extend(["--private-key", key])
        try:
            result = subprocess.run(
                command, cwd=self.root, text=True, capture_output=True, check=False, timeout=900
            )
        except FileNotFoundError as exc:
            raise RuntimeError("ansible-playbook is not installed") from exc
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError("Ansible worker configuration timed out") from exc
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout[-12000:],
            "stderr": result.stderr[-12000:],
        }
