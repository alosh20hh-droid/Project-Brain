from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ReplanDecision:
    should_replan: bool
    reason: str

def assess_replan(verification_accepted: bool, repeated_failure: bool, new_blocker: bool) -> ReplanDecision:
    if new_blocker:
        return ReplanDecision(True,"new blocker discovered")
    if repeated_failure:
        return ReplanDecision(True,"same approach is repeatedly failing")
    if not verification_accepted:
        return ReplanDecision(True,"result was not independently verified")
    return ReplanDecision(False,"continue current plan")
