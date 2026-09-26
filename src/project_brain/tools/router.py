from __future__ import annotations
from dataclasses import dataclass
from project_brain.contracts import ExecutionRequest,RiskLevel
from .registry import ToolRegistry
from .types import ToolResult

@dataclass(frozen=True)
class ToolCall:
 name:str
 arguments:dict

class ToolAuthorizationError(RuntimeError):pass

class ToolRouter:
 def __init__(self,registry:ToolRegistry)->None:self.registry=registry
 async def execute(self,request:ExecutionRequest,call:ToolCall)->ToolResult:
  if call.name not in request.allowed_actions:
   raise ToolAuthorizationError(f"tool not offered for task: {call.name}")
  spec=self.registry.spec(call.name)
  minimum=spec.minimum_risk
  if minimum is None and spec.kind.value=="external":minimum=RiskLevel.SENSITIVE
  rank={RiskLevel.LOW:0,RiskLevel.SENSITIVE:1,RiskLevel.IRREVERSIBLE:2}
  if minimum is not None and rank[request.risk]<rank[minimum]:raise ToolAuthorizationError("request risk understates tool risk")
  if spec.allowed_actions:
   raw=call.arguments.get("actions")
   if not isinstance(raw,list) or not raw:
    raise ToolAuthorizationError("explicit actions required for restricted tool")
   if not all(isinstance(x,str) for x in raw):
    raise ToolAuthorizationError("tool actions must be strings")
   if not set(raw).issubset(set(spec.allowed_actions)):
    raise ToolAuthorizationError("requested action exceeds tool capability")
  return await self.registry.call(call.name,call.arguments)
