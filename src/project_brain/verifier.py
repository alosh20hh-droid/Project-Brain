from .contracts import ExecutionRequest,ExecutionResult,VerificationResult
from .evidence import EvidenceRecord,EvidenceStrength,IndependentEvidenceVerifier
from .evidence.integrity import hash_payload

class EvidenceVerifier:
 def __init__(self)->None:self.independent=IndependentEvidenceVerifier()
 async def verify(self,request:ExecutionRequest,result:ExecutionResult)->VerificationResult:
  reasons=[]
  if result.task_id!=request.task_id:reasons.append("result belongs to a different task")
  if not result.completed:reasons.append("executor did not report completion")
  records=[]
  for index,e in enumerate(result.evidence):
   payload=e.content
   records.append(EvidenceRecord(
    id=f"{request.task_id}:{index}",task_id=result.task_id,kind=e.kind,source=e.source,
    payload=payload,content_hash=hash_payload(payload) if payload is not None else None,
    strength=EvidenceStrength.MEDIUM,
   ))
  required=[x.kind for x in request.evidence_required if x.required]
  verdict=self.independent.verify(required,records,task_id=request.task_id)
  reasons.extend(verdict.reasons)
  accepted=result.completed and result.task_id==request.task_id and verdict.accepted
  missing=[k for k in required if k not in {e.kind for e in result.evidence}]
  return VerificationResult(task_id=request.task_id,accepted=accepted,reasons=reasons,missing_evidence=missing)
