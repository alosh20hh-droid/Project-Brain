from __future__ import annotations
from dataclasses import dataclass
from project_brain.contracts import ExecutionRequest
from .registry import ToolRegistry
from .types import ToolResult

@dataclass(frozen=True)
class ToolCall:
    name:str
    arguments:dict

class ToolAuthorizationError(RuntimeError): pass

class ToolRouter:
    def __init__(self,registry:ToolRegistry)->None:
        self.registry=registry
    async def execute(self,request:ExecutionRequest,call:ToolCall)->ToolResult:
        if call.name not in request.allowed_actions:
            raise ToolAuthorizationError(f"tool not offered for task: {call.name}")
        spec=self.registry.spec(call.name)
        if spec.allowed_actions:
            requested=set(call.arguments.get("actions",[]))
            if not requested.issubset(set(spec.allowed_actions)):
                raise ToolAuthorizationError("requested action exceeds tool capability")
        return await self.registry.call(call.name,call.arguments)
