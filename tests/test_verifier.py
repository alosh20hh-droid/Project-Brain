import asyncio
from project_brain.contracts import Evidence, EvidenceRequirement, ExecutionRequest, ExecutionResult
from project_brain.verifier import EvidenceVerifier\nfrom project_brain.evidence.integrity import stable_hash

def test_verifier_rejects_missing_evidence():
    req = ExecutionRequest(task_id="t1", goal="test", evidence_required=[EvidenceRequirement(kind="receipt", description="proof")])
    result = ExecutionResult(task_id="t1", completed=True, summary="done")
    verdict = asyncio.run(EvidenceVerifier().verify(req, result))
    assert verdict.accepted is False
    assert verdict.missing_evidence == ["receipt"]

def test_verifier_accepts_completed_with_evidence():
    req = ExecutionRequest(task_id="t2", goal="test", evidence_required=[EvidenceRequirement(kind="log", description="proof")])
    result = ExecutionResult(task_id="t2", completed=True, summary="done", evidence=[Evidence(kind="log", source="executor", content="ok", content_hash=stable_hash("ok"), strength="supporting")])
    verdict = asyncio.run(EvidenceVerifier().verify(req, result))
    assert verdict.accepted is True


def test_verifier_rejects_executor_evidence_without_integrity_metadata():
 req=ExecutionRequest(task_id="t3",goal="test",evidence_required=[EvidenceRequirement(kind="log",description="proof")])
 result=ExecutionResult(task_id="t3",completed=True,summary="done",evidence=[Evidence(kind="log",source="executor",content="ok")])
 assert asyncio.run(EvidenceVerifier().verify(req,result)).accepted is False
