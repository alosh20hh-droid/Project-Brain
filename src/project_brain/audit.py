from __future__ import annotations
from dataclasses import dataclass,field
from datetime import datetime,timezone
from typing import Any

@dataclass(frozen=True)
class AuditEntry:
 actor:str
 action:str
 task_id:str|None=None
 details:dict[str,Any]=field(default_factory=dict)
 created_at:str=field(default_factory=lambda:datetime.now(timezone.utc).isoformat())

class AuditLog:
 def __init__(self)->None:self._entries:list[AuditEntry]=[]
 def append(self,entry:AuditEntry)->None:self._entries.append(entry)
 def all(self)->list[AuditEntry]:return list(self._entries)
