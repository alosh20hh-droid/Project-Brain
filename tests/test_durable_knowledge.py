from project_brain.bootstrap import bootstrap
from project_brain.evidence import EvidenceRecord,EvidenceStrength
from project_brain.long_term_memory import MemoryItem
from project_brain.evidence.integrity import stable_hash

def test_evidence_and_trusted_memory_survive_restart(tmp_path):
 db=tmp_path/"brain.db";first=bootstrap(db)
 evidence=EvidenceRecord(id="e1",task_id="t1",kind="result",source="executor",payload={"ok":True},content_hash=stable_hash({"ok":True}),collected_at="2026-09-26T00:00:00+00:00",strength=EvidenceStrength.STRONG)
 first.evidence.add(evidence)
 first.memory.add(MemoryItem(id="m1",project_id="p1",kind="verified_outcome",text="worked",evidence_refs=["e1"],verified=True))
 second=bootstrap(db)
 assert second.evidence.get("e1").task_id=="t1"
 assert [x.id for x in second.evidence.for_task("t1")]==["e1"]
 assert second.memory.get("m1").text=="worked"
 assert [x.id for x in second.memory.query("p1",trusted_only=True)]==["m1"]


def test_trusted_memory_rejects_missing_evidence(tmp_path):
 import pytest
 services=bootstrap(tmp_path/"missing.db")
 with pytest.raises(ValueError,match="missing evidence"):
  services.memory.add(MemoryItem(id="m",project_id="p",kind="fact",text="claim",evidence_refs=["does-not-exist"],verified=True))

def test_trusted_memory_rejects_tampered_evidence(tmp_path):
 import pytest
 services=bootstrap(tmp_path/"tampered.db")
 services.evidence.add(EvidenceRecord(id="bad",task_id="t",kind="result",source="executor",payload={"ok":False},content_hash=stable_hash({"ok":True}),collected_at="2026-09-26T00:00:00+00:00",strength=EvidenceStrength.STRONG))
 with pytest.raises(ValueError,match="invalid evidence"):
  services.memory.add(MemoryItem(id="m",project_id="p",kind="verified_outcome",text="worked",evidence_refs=["bad"],verified=True))

def test_trusted_memory_rejects_weak_evidence(tmp_path):
 import pytest
 services=bootstrap(tmp_path/"weak.db")
 services.evidence.add(EvidenceRecord(id="weak",task_id="t",kind="result",source="executor",payload="claim",content_hash=stable_hash("claim"),collected_at="2026-09-26T00:00:00+00:00",strength=EvidenceStrength.WEAK))
 with pytest.raises(ValueError,match="weak evidence"):
  services.memory.add(MemoryItem(id="m",project_id="p",kind="fact",text="claim",evidence_refs=["weak"],verified=True))
