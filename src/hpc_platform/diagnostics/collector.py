from __future__ import annotations
from pathlib import Path
class EvidenceCollector:
    def collect_log_tail(self,path:str,lines:int=200)->list[str]:
        p=Path(path)
        if not p.exists(): return []
        return p.read_text(errors='replace').splitlines()[-lines:]
