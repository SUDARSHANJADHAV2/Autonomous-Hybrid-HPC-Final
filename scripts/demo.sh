#!/usr/bin/env bash
set -euo pipefail
. .venv/bin/activate
hpcctl demo --event QUEUE_PRESSURE
hpcctl diagnose NODE_UNHEALTHY --node compute01
hpcctl incidents
