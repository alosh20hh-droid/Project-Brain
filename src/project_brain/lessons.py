from __future__ import annotations
from pydantic import BaseModel,Field

class Lesson(BaseModel):
 id:str
 project_id:str
 trigger:str
 lesson:str
 avoid:list[str]=Field(default_factory=list)
 prefer:list[str]=Field(default_factory=list)
 evidence_refs:list[str]=Field(default_factory=list)

class LessonBook:
 def __init__(self)->None:self._items:dict[str,Lesson]={}
 def add(self,item:Lesson)->None:self._items[item.id]=item
 def relevant(self,project_id:str,text:str)->list[Lesson]:
  words=set(text.lower().split())
  return [x for x in self._items.values() if x.project_id==project_id and words.intersection(x.trigger.lower().split())]
