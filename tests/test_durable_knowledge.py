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
