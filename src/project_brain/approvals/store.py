from __future__ import annotations
from datetime import datetime,timezone
import json
from project_brain.persistence import SQLiteProjectStore
from .types import ApprovalRequest,ApprovalStatus

class ApprovalStore:
 def __init__(self,store:SQLiteProjectStore|None=None)->None:self._items:dict[str,ApprovalRequest]={};self._consumed:set[str]=set();self.store=store
 def create(self,item:ApprovalRequest)->None:
  if self.store:
   if not self.store.put_if_absent("approval",item.id,item.model_dump(mode="json")):raise ValueError(f"duplicate approval: {item.id}")
  elif item.id in self._items:raise ValueError(f"duplicate approval: {item.id}")
  self._items[item.id]=item
 def get(self,item_id:str)->ApprovalRequest:
  if self.store:
   raw=self.store.get("approval",item_id)
   if raw is None:raise KeyError(item_id)
   return ApprovalRequest.model_validate(raw)
  return self._items[item_id]
 def _save(self,item:ApprovalRequest)->None:
  self._items[item.id]=item
  if self.store:self.store.put("approval",item.id,item.model_dump(mode="json"))
 def decide(self,item_id:str,approved:bool,actor:str)->ApprovalRequest:
  item=self.get(item_id)
  if item.status!=ApprovalStatus.PENDING:raise ValueError("approval already decided")
  item.status=ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED
  item.decided_by=actor;item.decided_at=datetime.now(timezone.utc).isoformat();self._save(item);return item
 def expire(self,item_id:str)->ApprovalRequest:
  item=self.get(item_id)
  if item.status in {ApprovalStatus.REJECTED,ApprovalStatus.EXPIRED}:return item
  item.status=ApprovalStatus.EXPIRED;self._save(item);return item
 def consume_and_reserve_operation(self,item_id:str,operation_id:str)->bool:
  if not self.store:return False
  now=datetime.now(timezone.utc)
  with self.store.connect() as db:
   db.execute("BEGIN IMMEDIATE")
   row=db.execute("SELECT value_json FROM kv WHERE namespace='approval' AND key=?",(item_id,)).fetchone()
   if row is None:return False
   item=ApprovalRequest.model_validate(json.loads(row[0]))
   if item.status!=ApprovalStatus.APPROVED or item.operation_id!=operation_id:return False
   if item.expires_at and datetime.fromisoformat(item.expires_at)<=now:return False
   if db.execute("SELECT 1 FROM kv WHERE namespace='approval_consumed' AND key=?",(item_id,)).fetchone():return False
   if db.execute("SELECT 1 FROM kv WHERE namespace='idempotency' AND key=?",(operation_id,)).fetchone():return False
   db.execute("INSERT INTO kv(namespace,key,value_json) VALUES('approval_consumed',?,?)",(item_id,json.dumps({"consumed_at":now.isoformat()},sort_keys=True)))
   db.execute("INSERT INTO kv(namespace,key,value_json) VALUES('idempotency',?,?)",(operation_id,json.dumps({"status":"reserved"},sort_keys=True)))
   return True
 def consumed(self,item_id:str)->bool:
  if self.store:return self.store.get("approval_consumed",item_id) is not None
  return item_id in self._consumed
 def consume(self,item_id:str)->bool:
  item=self.get(item_id)
  if item.status!=ApprovalStatus.APPROVED:return False
  if item.expires_at and datetime.fromisoformat(item.expires_at)<=datetime.now(timezone.utc):return False
  if self.store:return self.store.put_if_absent("approval_consumed",item_id,{"consumed_at":datetime.now(timezone.utc).isoformat()})
  if item_id in self._consumed:return False
  self._consumed.add(item_id);return True
