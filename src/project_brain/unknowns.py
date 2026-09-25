from __future__ import annotations
from enum import Enum
from pydantic import BaseModel

class UnknownPriority(str, Enum):
    LOW="low"
    MEDIUM="medium"
    HIGH="high"
    PROJECT_KILLER="project_killer"

class Unknown(BaseModel):
    id: str
    question: str
    why_it_matters: str
    priority: UnknownPriority = UnknownPriority.MEDIUM
    resolved: bool = False

def choose_next_unknown(items: list[Unknown]) -> Unknown | None:
    rank={UnknownPriority.PROJECT_KILLER:0,UnknownPriority.HIGH:1,UnknownPriority.MEDIUM:2,UnknownPriority.LOW:3}
    unresolved=[x for x in items if not x.resolved]
    return min(unresolved,key=lambda x:rank[x.priority]) if unresolved else None
