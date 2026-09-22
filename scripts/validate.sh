#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
python3 -m compileall -q src tests
PYTHONPATH="$ROOT/src" python3 -m pytest
python3 - <<'PY'
import json
from pathlib import Path
import yaml
for p in Path("schemas").glob("*.json"):
    json.loads(p.read_text(encoding="utf-8"))
for p in [Path("config/config.yaml"), Path("config/config.example.yaml"), Path("infrastructure/ansible/group_vars/all.yml")]:
    yaml.safe_load(p.read_text(encoding="utf-8"))
for p in Path("infrastructure/ansible").rglob("*.yml"):
    yaml.safe_load(p.read_text(encoding="utf-8"))
print("yaml/json ok")
PY
while IFS= read -r -d '' sh; do bash -n "$sh"; done < <(find "$ROOT" -name '*.sh' -not -path '*/.git/*' -print0)
python3 - <<'PY'
import re
from pathlib import Path
root=Path('.')
patterns=[re.compile(r'AKIA[0-9A-Z]{16}'), re.compile(r'-----BEGIN (?:RSA|OPENSSH|EC|DSA) PRIVATE KEY-----')]
for p in root.rglob('*'):
    if not p.is_file() or any(x in p.parts for x in {'.git','.venv','__pycache__','.pytest_cache'}): continue
    if p.suffix in {'.pyc','.db','.sqlite','.zip'}: continue
    try: text=p.read_text(encoding='utf-8',errors='ignore')
    except OSError: continue
    for rx in patterns:
        if rx.search(text): raise SystemExit(f'potential secret pattern: {p}')
print('secret-pattern scan ok')
PY
if command -v terraform >/dev/null 2>&1; then
  terraform -chdir=infrastructure/terraform/environments/demo fmt -check
  terraform -chdir=infrastructure/terraform/environments/demo init -backend=false -input=false -no-color >/dev/null
  terraform -chdir=infrastructure/terraform/environments/demo validate -no-color
else
  echo 'terraform not installed: validation deferred'
fi
if command -v ansible-playbook >/dev/null 2>&1; then
  ansible-galaxy collection install -r infrastructure/ansible/requirements.yml
  ansible-playbook -i infrastructure/ansible/inventory/local.ini infrastructure/ansible/playbooks/site.yml --syntax-check
else
  echo 'ansible not installed: validation deferred'
fi
