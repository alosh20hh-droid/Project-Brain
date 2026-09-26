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
  if self.store:
   raw=self.store.get("lease",task_id)
   if not raw:return None
   return Lease(task_id,raw["worker_id"],datetime.fromisoformat(raw["expires_at"]))
  return self._leases.get(task_id)
 def _save(self,item:Lease)->None:
  self._leases[item.task_id]=item
  if self.store:self.store.put("lease",item.task_id,{"worker_id":item.worker_id,"expires_at":item.expires_at.isoformat()})
 def claim(self,task_id:str,worker_id:str,seconds:int=120,now:datetime|None=None)->bool:
  if seconds<=0:raise ValueError("lease duration must be positive")
  now=now or datetime.now(timezone.utc);expires=now+timedelta(seconds=seconds)
  if self.store:
   with self.store.connect() as db:
    db.execute("BEGIN IMMEDIATE")
    row=db.execute("SELECT value_json FROM kv WHERE namespace=? AND key=?",("lease",task_id)).fetchone()
    if row:
     import json
     raw=json.loads(row[0]);current=Lease(task_id,raw["worker_id"],datetime.fromisoformat(raw["expires_at"]))
     if current.expires_at>now and current.worker_id!=worker_id:return False
    import json
    raw=json.dumps({"worker_id":worker_id,"expires_at":expires.isoformat()},sort_keys=True)
    db.execute("INSERT INTO kv(namespace,key,value_json) VALUES(?,?,?) ON CONFLICT(namespace,key) DO UPDATE SET value_json=excluded.value_json",("lease",task_id,raw))
   self._leases[task_id]=Lease(task_id,worker_id,expires);return True
  current=self._leases.get(task_id)
  if current and current.expires_at>now and current.worker_id!=worker_id:return False
  self._save(Lease(task_id,worker_id,expires));return True
 def renew(self,task_id:str,worker_id:str,seconds:int=120,now:datetime|None=None)->bool:
  if seconds<=0:raise ValueError("lease duration must be positive")
  now=now or datetime.now(timezone.utc);current=self._get(task_id)
  if not current or current.worker_id!=worker_id or current.expires_at<=now:return False
  return self.claim(task_id,worker_id,seconds,now)
 def expired(self,now:datetime|None=None)->list[Lease]:
  now=now or datetime.now(timezone.utc);ids=set(self._leases)
  if self.store:
   with self.store.connect() as db:ids.update(r[0] for r in db.execute("SELECT key FROM kv WHERE namespace='lease'"))
  return [x for task_id in ids if (x:=self._get(task_id)) and x.expires_at<=now]
 def release(self,task_id:str,worker_id:str)->bool:
  if self.store:
   with self.store.connect() as db:
    db.execute("BEGIN IMMEDIATE")
    row=db.execute("SELECT value_json FROM kv WHERE namespace=? AND key=?",("lease",task_id)).fetchone()
    if not row:return False
    import json
    raw=json.loads(row[0])
    if raw["worker_id"]!=worker_id:return False
    db.execute("DELETE FROM kv WHERE namespace=? AND key=?",("lease",task_id))
   self._leases.pop(task_id,None);return True
  current=self._leases.get(task_id)
  if not current or current.worker_id!=worker_id:return False
  del self._leases[task_id];return True
