from .contracts import ExecutionRequest, ExecutionResult, VerificationResult

class EvidenceVerifier:
    async def verify(self, request: ExecutionRequest, result: ExecutionResult) -> VerificationResult:
        available = {e.kind for e in result.evidence}
        missing = [r.kind for r in request.evidence_required if r.required and r.kind not in available]
        reasons = []
        if not result.completed:
            reasons.append("executor did not report completion")
        if missing:
            reasons.append("required evidence is missing")
        return VerificationResult(task_id=request.task_id, accepted=result.completed and not missing, reasons=reasons, missing_evidence=missing)
