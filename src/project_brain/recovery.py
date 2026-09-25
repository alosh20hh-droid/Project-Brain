from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class RetryDecision:
    retry: bool
    reason: str

def decide_retry(attempts: int, max_attempts: int, same_error_count: int)->RetryDecision:
    if attempts >= max_attempts:
        return RetryDecision(False,"attempt limit reached")
    if same_error_count >= 2:
        return RetryDecision(False,"repeated identical failure requires replanning")
    return RetryDecision(True,"retry allowed")
