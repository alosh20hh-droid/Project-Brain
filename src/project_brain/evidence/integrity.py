from __future__ import annotations
import hashlib,json
from typing import Any

def stable_hash(value:Any)->str:
 raw=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),default=str).encode("utf-8")
 return hashlib.sha256(raw).hexdigest()

def verify_hash(value:Any,expected:str)->bool:
 return stable_hash(value)==expected
