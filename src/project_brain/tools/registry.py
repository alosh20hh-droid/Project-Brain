from __future__ import annotations
from typing import Any,Awaitable,Callable
from .types import ToolSpec,ToolResult

ToolHandler=Callable[[dict[str,Any]],Awaitable[ToolResult]]

class ToolRegistry:
    def __init__(self)->None:
        self._specs:dict[str,ToolSpec]={}
        self._handlers:dict[str,ToolHandler]={}
    def register(self,spec:ToolSpec,handler:ToolHandler)->None:
        if spec.name in self._specs: raise ValueError(f"tool already registered: {spec.name}")
        self._specs[spec.name]=spec; self._handlers[spec.name]=handler
    def spec(self,name:str)->ToolSpec:
        if name not in self._specs: raise KeyError(f"unknown tool: {name}")
        return self._specs[name]
    async def call(self,name:str,args:dict[str,Any])->ToolResult:
        if name not in self._handlers: raise KeyError(f"unknown tool: {name}")
        return await self._handlers[name](args)
    def offered(self,allowed:list[str])->list[ToolSpec]:
        return [self._specs[n] for n in allowed if n in self._specs]
