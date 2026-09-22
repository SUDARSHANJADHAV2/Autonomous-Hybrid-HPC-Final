#!/usr/bin/env bash
set -euo pipefail
python3 -m compileall -q src
python3 -c 'from hpc_platform.storage.db import DB; DB("data/health.db").init(); print("database ok")'
