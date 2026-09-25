from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from .contracts import ExecutionRequest, ExecutionResult, VerificationResult
from .approval import require_owner_approval

class BrainPlanner(Protocol):
    async def next_request(self, state: dict) -> ExecutionRequest | None: ...
    async def learn(self, state: dict, request: ExecutionRequest, result: ExecutionResult, verification: VerificationResult) -> dict: ...

@dataclass
class CycleOutcome:
    state: dict
    request: ExecutionRequest | None
    result: ExecutionResult | None
    verification: VerificationResult | None
    status: str

class ProjectCycle:
    def __init__(self, planner: BrainPlanner, router, verifier) -> None:
        self.planner = planner
        self.router = router
        self.verifier = verifier

    async def run_once(self, state: dict, executor_name: str, owner_approved: bool = False) -> CycleOutcome:
        request = await self.planner.next_request(state)
        if request is None:
            return CycleOutcome(state, None, None, None, "idle")
        require_owner_approval(request, owner_approved)
        result = await self.router.execute(executor_name, request)
        verification = await self.verifier.verify(request, result)
        new_state = await self.planner.learn(state, request, result, verification)
        return CycleOutcome(new_state, request, result, verification, "accepted" if verification.accepted else "rejected")
