from __future__ import annotations
from pydantic import BaseModel, Field

class Decision(BaseModel):
    id: str
    question: str
    choice: str
    reasons: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    reversible: bool = True
