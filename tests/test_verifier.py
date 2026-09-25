import asyncio
from project_brain.contracts import Evidence, EvidenceRequirement, ExecutionRequest, ExecutionResult
from project_brain.verifier import EvidenceVerifier

def test_verifier_rejects_missing_evidence():
    req = ExecutionRequest(task_id="t1", goal="test", evidence_required=[EvidenceRequirement(kind="receipt", description="proof")])
    result = ExecutionResult(task_id="t1", completed=True, summary="done")
    verdict = asyncio.run(EvidenceVerifier().verify(req, result))
    assert verdict.accepted is False
    assert verdict.missing_evidence == ["receipt"]

def test_verifier_accepts_completed_with_evidence():
    req = ExecutionRequest(task_id="t2", goal="test", evidence_required=[EvidenceRequirement(kind="log", description="proof")])
    result = ExecutionResult(task_id="t2", completed=True, summary="done", evidence=[Evidence(kind="log", source="executor", content="ok")])
    verdict = asyncio.run(EvidenceVerifier().verify(req, result))
    assert verdict.accepted is True
