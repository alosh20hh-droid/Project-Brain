from __future__ import annotations
from pydantic import BaseModel, Field
from .unknowns import Unknown, choose_next_unknown
from .hypotheses import Hypothesis
from .experiments import Experiment, choose_cheapest

class Plan(BaseModel):
    focus_unknown_id: str | None = None
    hypothesis_ids: list[str] = Field(default_factory=list)
    experiment_id: str | None = None
    reason: str = ""

class PlanningEngine:
    def choose(self, unknowns: list[Unknown], hypotheses: list[Hypothesis], experiments: list[Experiment]) -> Plan:
        unknown = choose_next_unknown(unknowns)
        if unknown is None:
            return Plan(reason="no unresolved unknown")
        hs=[h for h in hypotheses if h.status.value=="open"]
        ex=choose_cheapest([e for e in experiments if any(h.id==e.hypothesis_id for h in hs)])
        return Plan(focus_unknown_id=unknown.id,hypothesis_ids=[h.id for h in hs],experiment_id=ex.id if ex else None,reason="reduce highest-risk unknown with cheapest useful experiment")
