from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, Field

class HypothesisStatus(str, Enum):
    OPEN = "open"
    TESTING = "testing"
    SUPPORTED = "supported"
    REJECTED = "rejected"

class Hypothesis(BaseModel):
    id: str
    statement: str
    why_it_matters: str
    cheapest_test: str
    success_condition: str
    failure_condition: str
    status: HypothesisStatus = HypothesisStatus.OPEN
    evidence_ids: list[str] = Field(default_factory=list)
