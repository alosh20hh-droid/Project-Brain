from __future__ import annotations
from datetime import datetime,timezone
from typing import Any
from pydantic import BaseModel,Field

class MemoryItem(BaseModel):
 id:str
 project_id:str
 kind:str
 text:str
 tags:list[str]=Field(default_factory=list)
 evidence_refs:list[str]=Field(default_factory=list)
 confidence:float=1.0
 created_at:str=Field(default_factory=lambda:datetime.now(timezone.utc).isoformat())
 supersedes:str|None=None

class LongTermMemory:
 def __init__(self)->None:self._items:dict[str,MemoryItem]={}
 def add(self,item:MemoryItem)->None:
  if item.id in self._items: raise ValueError(f"duplicate memory id: {item.id}")
  self._items[item.id]=item
 def get(self,item_id:str)->MemoryItem:return self._items[item_id]
 def query(self,project_id:str,kinds:list[str]|None=None,tags:list[str]|None=None)->list[MemoryItem]:
  items=[x for x in self._items.values() if x.project_id==project_id]
  if kinds: items=[x for x in items if x.kind in kinds]
  if tags:
   wanted=set(tags); items=[x for x in items if wanted.intersection(x.tags)]
  superseded={x.supersedes for x in items if x.supersedes}
  return [x for x in items if x.id not in superseded]
