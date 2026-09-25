from __future__ import annotations
from .types import EvidenceRecord

class EvidenceStore:
 def __init__(self)->None: self._items:dict[str,EvidenceRecord]={}
 def add(self,item:EvidenceRecord)->None:
  if item.id in self._items: raise ValueError(f"duplicate evidence id: {item.id}")
  self._items[item.id]=item
 def get(self,evidence_id:str)->EvidenceRecord: return self._items[evidence_id]
 def for_task(self,task_id:str)->list[EvidenceRecord]:
  return [x for x in self._items.values() if x.task_id==task_id]
