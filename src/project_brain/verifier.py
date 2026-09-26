from datetime import datetime,timezone
from .contracts import ExecutionRequest,ExecutionResult,VerificationResult
from .evidence import EvidenceRecord,EvidenceStrength,IndependentEvidenceVerifier

class EvidenceVerifier:
 def __init__(self)->None:self.independent=IndependentEvidenceVerifier()
 async def verify(self,request:ExecutionRequest,result:ExecutionResult)->VerificationResult:
  reasons=[]
  if result.task_id!=request.task_id:reasons.append("result belongs to a different task")
  if not result.completed:reasons.append("executor did not report completion")
  records=[]
  for index,e in enumerate(result.evidence):
   try:strength=EvidenceStrength(e.strength)
   except ValueError:strength=EvidenceStrength.WEAK
   records.append(EvidenceRecord(
    id=f"{request.task_id}:{index}",task_id=result.task_id,kind=e.kind,source=e.source,
    payload=e.content,uri=e.uri,content_hash=e.content_hash,
    collected_at=e.collected_at or datetime.now(timezone.utc).isoformat(),strength=strength,
   ))
  required=[x.kind for x in request.evidence_required if x.required]
  verdict=self.independent.verify(required,records,task_id=request.task_id)
  reasons.extend(verdict.reasons)
  accepted=result.completed and result.task_id==request.task_id and verdict.accepted
  accepted_kinds={r.kind for r in records if r.id in verdict.accepted_ids}
  missing=[k for k in required if k not in accepted_kinds]
  return VerificationResult(task_id=request.task_id,accepted=accepted,reasons=reasons,missing_evidence=missing)
