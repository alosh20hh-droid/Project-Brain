from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Lock:
 resource:str
 owner:str

class LockManager:
 def __init__(self)->None:self._locks:dict[str,Lock]={}
 def acquire(self,resource:str,owner:str)->bool:
  current=self._locks.get(resource)
  if current and current.owner!=owner:return False
  self._locks[resource]=Lock(resource,owner);return True
 def release(self,resource:str,owner:str)->bool:
  current=self._locks.get(resource)
  if not current or current.owner!=owner:return False
  del self._locks[resource];return True
 def owner(self,resource:str)->str|None:
  lock=self._locks.get(resource);return lock.owner if lock else None
