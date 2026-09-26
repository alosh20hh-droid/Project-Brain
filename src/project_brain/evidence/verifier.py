from __future__ import annotations
from dataclasses import dataclass,field
from .types import EvidenceRecord,EvidenceStrength
from .integrity import verify_hash

@dataclass
class EvidenceVerdict:
 accepted:bool
 reasons:list[str]=field(default_factory=list)
 accepted_ids:list[str]=field(default_factory=list)
 rejected_ids:list[str]=field(default_factory=list)

class IndependentEvidenceVerifier:
 def verify(self,required_kinds:list[str],records:list[EvidenceRecord],task_id:str|None=None)->EvidenceVerdict:
  reasons=[];accepted=[];rejected=[];valid=[]
  for r in records:
   if task_id is not None and r.task_id!=task_id:
    rejected.append(r.id);reasons.append(f"wrong task: {r.id}");continue
   if r.payload is None and r.uri:
    rejected.append(r.id);reasons.append(f"unsealed uri evidence: {r.id}");continue
   if r.payload is None and not r.uri:
    rejected.append(r.id);reasons.append(f"empty evidence: {r.id}");continue
   if r.payload is not None and not r.content_hash:
    rejected.append(r.id);reasons.append(f"missing integrity hash: {r.id}");continue
   if r.content_hash and not verify_hash(r.payload,r.content_hash):
    rejected.append(r.id);reasons.append(f"integrity failure: {r.id}");continue
   if r.strength==EvidenceStrength.WEAK:
    rejected.append(r.id);reasons.append(f"weak evidence: {r.id}");continue
   valid.append(r);accepted.append(r.id)
  kinds={r.kind for r in valid}
  missing=[k for k in required_kinds if k not in kinds]
  if missing:reasons.append("missing required evidence: "+",".join(missing))
  return EvidenceVerdict(not missing and not rejected,reasons,accepted,rejected)
