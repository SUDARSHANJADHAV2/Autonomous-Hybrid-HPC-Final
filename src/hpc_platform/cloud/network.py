from __future__ import annotations

import shutil
import socket
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class NetworkResult:
    connected: bool
    detail: str = ""


class NetworkProvider:
    def connect(self, node: str) -> NetworkResult:  # pragma: no cover - interface
        raise NotImplementedError


class DirectSSHProvider(NetworkProvider):
    def __init__(self, port: int = 22, timeout: float = 5.0):
        self.port = port
        self.timeout = timeout

    def connect(self, node: str) -> NetworkResult:
        try:
            with socket.create_connection((node, self.port), timeout=self.timeout):
                return NetworkResult(True, f"TCP {self.port} reachable on {node}")
        except OSError as exc:
            return NetworkResult(False, f"TCP {self.port} unreachable on {node}: {exc}")


class TailscaleProvider(NetworkProvider):
    def __init__(self, timeout: int = 15):
        self.timeout = timeout

    def connect(self, node: str) -> NetworkResult:
        binary = shutil.which("tailscale")
        if binary is None:
            return NetworkResult(False, "tailscale CLI is not installed")
        try:
            result = subprocess.run(
                [binary, "ping", "--c", "1", node],
                text=True,
                capture_output=True,
                check=False,
                timeout=self.timeout,
            )
        except subprocess.TimeoutExpired:
            return NetworkResult(False, f"Tailscale ping timed out for {node}")
        detail = (result.stdout or result.stderr).strip()
        return NetworkResult(result.returncode == 0, detail)
