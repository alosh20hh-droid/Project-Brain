from __future__ import annotations
from .memory import MemoryStore, OutcomeMemory
from .contracts import ExecutionRequest, ExecutionResult, VerificationResult

class OutcomeLearner:
    def __init__(self, memory: MemoryStore) -> None:
        self.memory=memory

    def record(self, request: ExecutionRequest, result: ExecutionResult, verification: VerificationResult) -> None:
        lessons=[]
        if not verification.accepted:
            lessons.extend(verification.reasons or ["result rejected"])
        if result.error:
            lessons.append(result.error)
        self.memory.add(OutcomeMemory(task_id=request.task_id,decision=request.goal,outcome=result.summary,accepted=verification.accepted,lessons=lessons,evidence_refs=[e.uri for e in result.evidence if e.uri]))
