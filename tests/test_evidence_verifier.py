from datetime import datetime,timezone
from project_brain.evidence import EvidenceRecord,EvidenceStrength,IndependentEvidenceVerifier,stable_hash

def rec(id,kind,payload,strength=EvidenceStrength.STRONG,bad=False):
 h=stable_hash(payload)
 if bad:h="0"*64
 return EvidenceRecord(id=id,task_id="t",kind=kind,source="test",payload=payload,content_hash=h,collected_at=datetime.now(timezone.utc).isoformat(),strength=strength)

def test_accepts_required_strong_evidence():
 v=IndependentEvidenceVerifier().verify(["source"],[rec("e1","source",{"ok":True})])
 assert v.accepted

def test_rejects_tampered_evidence():
 v=IndependentEvidenceVerifier().verify(["source"],[rec("e1","source",{"ok":True},bad=True)])
 assert not v.accepted
 assert "e1" in v.rejected_ids

def test_weak_evidence_cannot_certify():
 v=IndependentEvidenceVerifier().verify(["source"],[rec("e1","source","claim",EvidenceStrength.WEAK)])
 assert not v.accepted
