from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, Field

class GoalStatus(str, Enum):
    ACTIVE="active"
    BLOCKED="blocked"
    ACHIEVED="achieved"
    ABANDONED="abandoned"

class Goal(BaseModel):
    id: str
    statement: str
    success_conditions: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    status: GoalStatus = GoalStatus.ACTIVE
