from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime,timezone

@dataclass
class Worker:
 id:str
 capabilities:set[str]
 busy:bool=False
 last_heartbeat:str|None=None
 def heartbeat(self)->None:self.last_heartbeat=datetime.now(timezone.utc).isoformat()

class WorkerPool:
 def __init__(self)->None:self._workers:dict[str,Worker]={}
 def register(self,worker:Worker)->None:self._workers[worker.id]=worker
 def eligible(self,required:set[str])->list[Worker]:
  return [w for w in self._workers.values() if not w.busy and required.issubset(w.capabilities)]
