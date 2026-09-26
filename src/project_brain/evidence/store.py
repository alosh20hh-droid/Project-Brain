from __future__ import annotations
from project_brain.persistence import SQLiteProjectStore
from .types import EvidenceRecord

class EvidenceStore:
 def __init__(self,store:SQLiteProjectStore|None=None)->None:
  self._items:dict[str,EvidenceRecord]={};self.store=store
 def add(self,item:EvidenceRecord)->None:
  if self.store:
   if not self.store.put_if_absent("evidence",item.id,item.model_dump(mode="json")):raise ValueError(f"duplicate evidence id: {item.id}")
  elif item.id in self._items:raise ValueError(f"duplicate evidence id: {item.id}")
  self._items[item.id]=item
 def get(self,evidence_id:str)->EvidenceRecord:
  if self.store:
   raw=self.store.get("evidence",evidence_id)
   if raw is None:raise KeyError(evidence_id)
   return EvidenceRecord.model_validate(raw)
  return self._items[evidence_id]
 def for_task(self,task_id:str)->list[EvidenceRecord]:
  if self.store:
   with self.store.connect() as db:
    rows=db.execute("SELECT value_json FROM kv WHERE namespace='evidence'").fetchall()
   import json
   return [x for row in rows if (x:=EvidenceRecord.model_validate(json.loads(row[0]))).task_id==task_id]
  return [x for x in self._items.values() if x.task_id==task_id]
