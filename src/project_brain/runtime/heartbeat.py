from __future__ import annotations
from datetime import datetime,timezone,timedelta
from dataclasses import dataclass

@dataclass
class Heartbeat:
 worker_id:str
 seen_at:datetime

class HeartbeatMonitor:
 def __init__(self,timeout_seconds:int=90)->None:
  self.timeout=timedelta(seconds=timeout_seconds);self._beats:dict[str,Heartbeat]={}
 def beat(self,worker_id:str,at:datetime|None=None)->None:
  self._beats[worker_id]=Heartbeat(worker_id,at or datetime.now(timezone.utc))
 def alive(self,worker_id:str,now:datetime|None=None)->bool:
  h=self._beats.get(worker_id)
  if not h:return False
  return (now or datetime.now(timezone.utc))-h.seen_at<=self.timeout
 def dead_workers(self,now:datetime|None=None)->list[str]:
  return [wid for wid in self._beats if not self.alive(wid,now)]
