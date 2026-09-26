from __future__ import annotations
from .sqlite import SQLiteProjectStore

class IdempotencyStore:
 def __init__(self,store:SQLiteProjectStore)->None:self.store=store
 def reserve(self,key:str)->bool:
  return self.store.put_if_absent("idempotency",key,{"status":"reserved"})
 def complete(self,key:str,result_ref:str|None=None)->None:
  current=self.status(key)
  if current is None:raise RuntimeError("cannot complete an unreserved action")
  if current.get("status")=="completed":return
  if current.get("status")!="reserved":raise RuntimeError("invalid idempotency state")
  self.store.put("idempotency",key,{"status":"completed","result_ref":result_ref})
 def status(self,key:str):return self.store.get("idempotency",key)
