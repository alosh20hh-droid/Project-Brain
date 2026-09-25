from __future__ import annotations
from dataclasses import dataclass
from .contracts import ExecutionRequest, RiskLevel

@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    requires_owner_approval: bool
    reason: str

class ActionPolicy:
    def evaluate(self, request: ExecutionRequest) -> PolicyDecision:
        if request.risk in {RiskLevel.SENSITIVE, RiskLevel.IRREVERSIBLE}:
            return PolicyDecision(True, True, "owner approval required")
        return PolicyDecision(True, False, "low-risk action")
