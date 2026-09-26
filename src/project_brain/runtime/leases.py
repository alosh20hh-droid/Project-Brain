from __future__ import annotations
from datetime import datetime,timezone,timedelta
from dataclasses import dataclass
from project_brain.persistence import SQLiteProjectStore

@dataclass(frozen=True)
class Lease:
 task_id:str
 worker_id:str
 expires_at:datetime

class LeaseManager:
 def __init__(self,store:SQLiteProjectStore|None=None)->None:self._leases:dict[str,Lease]={};self.store=store
 def _get(self,task_id:str)->Lease|None:
  item=self._leases.get(task_id)
  if item or not self.store:return item
  raw=self.store.get("lease",task_id)
  if not raw:return None
  item=Lease(task_id,raw["worker_id"],datetime.fromisoformat(raw["expires_at"]));self._leases[task_id]=item;return item
 def _save(self,item:Lease)->None:
  self._leases[item.task_id]=item
  if self.store:self.store.put("lease",item.task_id,{"worker_id":item.worker_id,"expires_at":item.expires_at.isoformat()})
 def claim(self,task_id:str,worker_id:str,seconds:int=120,now:datetime|None=None)->bool:
  if seconds<=0:raise ValueError("lease duration must be positive")
  now=now or datetime.now(timezone.utc);current=self._get(task_id)
  if current and current.expires_at>now and current.worker_id!=worker_id:return False
  self._save(Lease(task_id,worker_id,now+timedelta(seconds=seconds)));return True
 def renew(self,task_id:str,worker_id:str,seconds:int=120,now:datetime|None=None)->bool:
  if seconds<=0:raise ValueError("lease duration must be positive")
  current=self._get(task_id)
  if not current or current.worker_id!=worker_id:return False
  now=now or datetime.now(timezone.utc)
  if current.expires_at<=now:return False
  self._save(Lease(task_id,worker_id,now+timedelta(seconds=seconds)));return True
 def expired(self,now:datetime|None=None)->list[Lease]:
  now=now or datetime.now(timezone.utc);ids=set(self._leases)
  if self.store:
   with self.store.connect() as db:ids.update(r[0] for r in db.execute("SELECT key FROM kv WHERE namespace='lease'"))
  return [x for task_id in ids if (x:=self._get(task_id)) and x.expires_at<=now]
 def release(self,task_id:str,worker_id:str)->bool:
  current=self._get(task_id)
  if not current or current.worker_id!=worker_id:return False
  self._leases.pop(task_id,None)
  if self.store:
   with self.store.connect() as db:db.execute("DELETE FROM kv WHERE namespace=? AND key=?",("lease",task_id))
  return True
