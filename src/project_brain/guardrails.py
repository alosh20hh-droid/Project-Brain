from __future__ import annotations
from dataclasses import dataclass
from .contracts import ExecutionRequest, RiskLevel

@dataclass(frozen=True)
class GuardrailResult:
    allowed: bool
    reason: str

class Guardrails:
    def check(self, request: ExecutionRequest) -> GuardrailResult:
        if not request.goal.strip():
            return GuardrailResult(False,"empty goal")
        if request.timeout_seconds <= 0:
            return GuardrailResult(False,"invalid timeout")
        if request.risk == RiskLevel.IRREVERSIBLE:
            return GuardrailResult(False,"irreversible actions must pass the owner approval gateway")
        return GuardrailResult(True,"allowed")
