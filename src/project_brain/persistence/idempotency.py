from __future__ import annotations
from .sqlite import SQLiteProjectStore

class IdempotencyStore:
 def __init__(self,store:SQLiteProjectStore)->None:self.store=store
 def reserve(self,key:str)->bool:
  if self.store.get("idempotency",key) is not None:return False
  self.store.put("idempotency",key,{"status":"reserved"}); return True
 def complete(self,key:str,result_ref:str|None=None)->None:
  self.store.put("idempotency",key,{"status":"completed","result_ref":result_ref})
 def status(self,key:str):return self.store.get("idempotency",key)
