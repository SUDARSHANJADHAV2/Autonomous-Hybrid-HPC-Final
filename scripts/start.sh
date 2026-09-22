#!/usr/bin/env bash
set -euo pipefail
. .venv/bin/activate
uvicorn hpc_platform.api.app:app --host 127.0.0.1 --port 8000
