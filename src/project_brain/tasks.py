from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, Field

class TaskStatus(str, Enum):
    READY="ready"
    RUNNING="running"
    WAITING_APPROVAL="waiting_approval"
    VERIFYING="verifying"
    DONE="done"
    FAILED="failed"
    BLOCKED="blocked"

class Task(BaseModel):
    id: str
    goal_id: str
    title: str
    reason: str
    hypothesis_id: str | None = None
    required_evidence: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.READY
