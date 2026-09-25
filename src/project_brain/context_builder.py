from __future__ import annotations
from typing import Any
from .long_term_memory import LongTermMemory

class ContextBuilder:
 def __init__(self,memory:LongTermMemory,max_items:int=20)->None:
  self.memory=memory; self.max_items=max_items
 def build(self,project_id:str,state:dict[str,Any],tags:list[str]|None=None)->dict[str,Any]:
  items=self.memory.query(project_id,tags=tags)
  items=sorted(items,key=lambda x:(x.confidence,x.created_at),reverse=True)[:self.max_items]
  return {"project_id":project_id,"state":state,"memories":[x.model_dump() for x in items]}
