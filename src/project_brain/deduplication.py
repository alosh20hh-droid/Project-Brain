from __future__ import annotations
import hashlib

def work_fingerprint(goal:str,action:str,constraints:list[str]|None=None)->str:
 raw="|".join([goal.strip().lower(),action.strip().lower(),*(sorted(x.strip().lower() for x in (constraints or [])))])
 return hashlib.sha256(raw.encode("utf-8")).hexdigest()

class WorkHistory:
 def __init__(self)->None:self._done:set[str]=set()
 def mark(self,fingerprint:str)->None:self._done.add(fingerprint)
 def seen(self,fingerprint:str)->bool:return fingerprint in self._done
