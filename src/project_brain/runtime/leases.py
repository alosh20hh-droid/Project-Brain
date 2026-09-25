from __future__ import annotations
from datetime import datetime,timezone,timedelta
from dataclasses import dataclass

@dataclass(frozen=True)
class Lease:
 task_id:str
 worker_id:str
 expires_at:datetime

class LeaseManager:
 def __init__(self)->None:self._leases:dict[str,Lease]={}
 def claim(self,task_id:str,worker_id:str,seconds:int=120,now:datetime|None=None)->bool:
  if seconds<=0:raise ValueError("lease duration must be positive")
  now=now or datetime.now(timezone.utc);current=self._leases.get(task_id)
  if current and current.expires_at>now and current.worker_id!=worker_id:return False
  self._leases[task_id]=Lease(task_id,worker_id,now+timedelta(seconds=seconds));return True
 def renew(self,task_id:str,worker_id:str,seconds:int=120,now:datetime|None=None)->bool:
  if seconds<=0:raise ValueError("lease duration must be positive")
  current=self._leases.get(task_id)
  if not current or current.worker_id!=worker_id:return False
  now=now or datetime.now(timezone.utc)
  if current.expires_at<=now:return False
  self._leases[task_id]=Lease(task_id,worker_id,now+timedelta(seconds=seconds));return True
 def expired(self,now:datetime|None=None)->list[Lease]:
  now=now or datetime.now(timezone.utc)
  return [x for x in self._leases.values() if x.expires_at<=now]
 def release(self,task_id:str,worker_id:str)->bool:
  current=self._leases.get(task_id)
  if not current or current.worker_id!=worker_id:return False
  del self._leases[task_id];return True
