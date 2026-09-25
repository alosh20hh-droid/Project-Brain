from __future__ import annotations
from pydantic import BaseModel, Field

class Experiment(BaseModel):
    id: str
    hypothesis_id: str
    action: str
    expected_cost: float = 0.0
    expected_minutes: int = 0
    required_evidence: list[str] = Field(default_factory=list)

def choose_cheapest(experiments: list[Experiment]) -> Experiment | None:
    if not experiments:
        return None
    return min(experiments, key=lambda x: (x.expected_cost, x.expected_minutes))
