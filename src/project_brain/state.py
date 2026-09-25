from __future__ import annotations
from pydantic import BaseModel, Field

class ProjectState(BaseModel):
    project_id: str
    goal: str
    knowns: list[str] = Field(default_factory=list)
    unknowns: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    decisions: list[str] = Field(default_factory=list)
    failures: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
