from __future__ import annotations
from datetime import datetime,timezone,timedelta
from dataclasses import dataclass
from project_brain.persistence import SQLiteProjectStore

@dataclass
class Heartbeat:
 worker_id:str
 seen_at:datetime

class HeartbeatMonitor:
 def __init__(self,timeout_seconds:int=90,store:SQLiteProjectStore|None=None)->None:
  self.timeout=timedelta(seconds=timeout_seconds);self._beats:dict[str,Heartbeat]={};self.store=store
 def beat(self,worker_id:str,at:datetime|None=None)->None:
  seen=at or datetime.now(timezone.utc);self._beats[worker_id]=Heartbeat(worker_id,seen)
  if self.store:self.store.put("heartbeat",worker_id,{"seen_at":seen.isoformat()})
 def _get(self,worker_id:str)->Heartbeat|None:
  h=self._beats.get(worker_id)
  if h or not self.store:return h
  raw=self.store.get("heartbeat",worker_id)
  if not raw:return None
  h=Heartbeat(worker_id,datetime.fromisoformat(raw["seen_at"]));self._beats[worker_id]=h;return h
 def alive(self,worker_id:str,now:datetime|None=None)->bool:
  h=self._get(worker_id)
  if not h:return False
  return (now or datetime.now(timezone.utc))-h.seen_at<=self.timeout
 def dead_workers(self,now:datetime|None=None)->list[str]:
  ids=set(self._beats)
  if self.store:
   with self.store.connect() as db:
    ids.update(r[0] for r in db.execute("SELECT key FROM kv WHERE namespace='heartbeat'"))
  return [wid for wid in ids if not self.alive(wid,now)]
