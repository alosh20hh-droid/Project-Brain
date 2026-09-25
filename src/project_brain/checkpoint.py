from __future__ import annotations
import json
from pathlib import Path
from typing import Any

class JsonCheckpointStore:
    def __init__(self, path: str | Path) -> None:
        self.path=Path(path)

    def save(self, state: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True,exist_ok=True)
        tmp=self.path.with_suffix(self.path.suffix+".tmp")
        tmp.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
        tmp.replace(self.path)

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))
