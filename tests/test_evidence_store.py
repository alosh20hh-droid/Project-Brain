import pytest
from datetime import datetime,timezone
from project_brain.evidence import EvidenceStore,EvidenceRecord

def test_duplicate_evidence_is_rejected():
 s=EvidenceStore(); e=EvidenceRecord(id="e",task_id="t",kind="log",source="x",collected_at=datetime.now(timezone.utc).isoformat())
 s.add(e)
 with pytest.raises(ValueError):s.add(e)
