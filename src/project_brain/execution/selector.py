from __future__ import annotations
from project_brain.tools.types import ToolKind

DEFAULT_EXECUTORS={
    ToolKind.INTERNAL:"internal",
    ToolKind.RESEARCH:"research",
    ToolKind.FILE:"files",
    ToolKind.BROWSER:"browser",
    ToolKind.EXTERNAL:"external",
}

def select_executor(kind:ToolKind,overrides:dict[ToolKind,str]|None=None)->str:
    mapping={**DEFAULT_EXECUTORS,**(overrides or {})}
    return mapping[kind]
