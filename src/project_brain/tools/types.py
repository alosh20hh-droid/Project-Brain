from __future__ import annotations
from enum import Enum
from typing import Any
from pydantic import BaseModel,Field
from project_brain.contracts import RiskLevel

class ToolKind(str,Enum):
 INTERNAL="internal";RESEARCH="research";FILE="file";BROWSER="browser";EXTERNAL="external"

class ToolSpec(BaseModel):
 name:str
 kind:ToolKind
 description:str
 allowed_actions:list[str]=Field(default_factory=list)
 minimum_risk:RiskLevel|None=None

class ToolResult(BaseModel):
 ok:bool
 summary:str
 data:dict[str,Any]=Field(default_factory=dict)
 evidence:list[dict[str,Any]]=Field(default_factory=list)
 error:str|None=None
