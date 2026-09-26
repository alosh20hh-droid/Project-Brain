from __future__ import annotations
from datetime import datetime,timezone
from typing import Any
from .persistence import SQLiteProjectStore
import json
from pydantic import BaseModel,Field,model_validator

TRUSTED_KINDS={"fact","decision","verified_outcome"}

class MemoryItem(BaseModel):
 id:str
 project_id:str
 kind:str
 text:str
 tags:list[str]=Field(default_factory=list)
 evidence_refs:list[str]=Field(default_factory=list)
 confidence:float=1.0
 verified:bool=False
 created_at:str=Field(default_factory=lambda:datetime.now(timezone.utc).isoformat())
 supersedes:str|None=None

 @model_validator(mode="after")
 def validate_trust(self):
  if not 0<=self.confidence<=1:raise ValueError("confidence must be between 0 and 1")
  if self.kind in TRUSTED_KINDS and (not self.verified or not self.evidence_refs):
   raise ValueError("trusted memory requires verification and evidence")
  return self

class LongTermMemory:
 def __init__(self,store:SQLiteProjectStore|None=None)->None:self._items:dict[str,MemoryItem]={};self.store=store
 def add(self,item:MemoryItem)->None:
  if self.store:
   if self.store.get("memory",item.id) is not None:raise ValueError(f"duplicate memory id: {item.id}")
  elif item.id in self._items:raise ValueError(f"duplicate memory id: {item.id}")
  if item.supersedes:
   old=self.get(item.supersedes) if self.store and self.store.get("memory",item.supersedes) is not None else self._items.get(item.supersedes)
   if old is None:raise ValueError("superseded memory does not exist")
   if old.project_id!=item.project_id:raise ValueError("cannot supersede memory from another project")
  self._items[item.id]=item
  if self.store:self.store.put("memory",item.id,item.model_dump(mode="json"))
 def get(self,item_id:str)->MemoryItem:
  if self.store:
   raw=self.store.get("memory",item_id)
   if raw is None:raise KeyError(item_id)
   return MemoryItem.model_validate(raw)
  return self._items[item_id]
 def query(self,project_id:str,kinds:list[str]|None=None,tags:list[str]|None=None,trusted_only:bool=False)->list[MemoryItem]:
  if self.store:
   with self.store.connect() as db:rows=db.execute("SELECT value_json FROM kv WHERE namespace=\'memory\'").fetchall()
   source=[MemoryItem.model_validate(json.loads(row[0])) for row in rows]
  else:source=list(self._items.values())
  items=[x for x in source if x.project_id==project_id]
  if kinds:items=[x for x in items if x.kind in kinds]
  if tags:
   wanted=set(tags);items=[x for x in items if wanted.intersection(x.tags)]
  if trusted_only:items=[x for x in items if x.verified and bool(x.evidence_refs)]
  superseded={x.supersedes for x in items if x.supersedes}
  return [x for x in items if x.id not in superseded]
