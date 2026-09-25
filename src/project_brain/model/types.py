from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field

class ModelMessage(BaseModel):
    role: str
    content: str

class ModelToolCall(BaseModel):
    id: str
    name: str
    arguments: dict[str,Any]=Field(default_factory=dict)

class ModelResponse(BaseModel):
    text: str=""
    tool_calls: list[ModelToolCall]=Field(default_factory=list)
    usage: dict[str,Any]=Field(default_factory=dict)
    raw: dict[str,Any]|None=None
