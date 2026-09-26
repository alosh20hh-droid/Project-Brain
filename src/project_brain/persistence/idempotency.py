from __future__ import annotations
import json
from .sqlite import SQLiteProjectStore

class IdempotencyStore:
 def __init__(self,store:SQLiteProjectStore)->None:self.store=store
 def reserve(self,key:str,metadata:dict|None=None)->bool:
  value=dict(metadata or {})
  value["status"]="reserved"
  return self.store.put_if_absent("idempotency",key,value)
 def complete(self,key:str,result_ref:str|None=None)->None:
  with self.store.connect() as db:
   db.execute("BEGIN IMMEDIATE")
   row=db.execute("SELECT value_json FROM kv WHERE namespace=? AND key=?",("idempotency",key)).fetchone()
   if row is None:raise RuntimeError("cannot complete an unreserved action")
   current=json.loads(row[0])
   if current.get("status")=="completed":return
   if current.get("status")!="reserved":raise RuntimeError("invalid idempotency state")
   current["status"]="completed";current["result_ref"]=result_ref
   db.execute("UPDATE kv SET value_json=? WHERE namespace=? AND key=?",(json.dumps(current,ensure_ascii=False,sort_keys=True),"idempotency",key))
 def status(self,key:str):return self.store.get("idempotency",key)
