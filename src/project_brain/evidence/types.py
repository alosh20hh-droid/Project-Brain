from __future__ import annotations
from enum import Enum
from typing import Any
from pydantic import BaseModel,Field

class EvidenceStrength(str,Enum):
 WEAK="weak"; SUPPORTING="supporting"; STRONG="strong"

class EvidenceRecord(BaseModel):
 id:str
 task_id:str
 kind:str
 source:str
 payload:Any|None=None
 uri:str|None=None
 content_hash:str|None=None
 collected_at:str
 strength:EvidenceStrength=EvidenceStrength.SUPPORTING
 metadata:dict[str,Any]=Field(default_factory=dict)
