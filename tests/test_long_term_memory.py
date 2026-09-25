import pytest
from project_brain.long_term_memory import LongTermMemory,MemoryItem
from project_brain.context_builder import ContextBuilder

def trusted(id,project_id,text,supersedes=None):
 return MemoryItem(id=id,project_id=project_id,kind="fact",text=text,verified=True,evidence_refs=["e1"],supersedes=supersedes)

def test_new_memory_can_supersede_old_memory():
 m=LongTermMemory();m.add(trusted("old","p","A"));m.add(trusted("new","p","B","old"))
 assert [x.id for x in m.query("p")]==["new"]

def test_projects_are_isolated():
 m=LongTermMemory();m.add(trusted("a","p1","x"));m.add(trusted("b","p2","y"))
 assert [x.id for x in m.query("p1")]==["a"]

def test_unverified_fact_cannot_enter_trusted_memory():
 with pytest.raises(ValueError):MemoryItem(id="bad",project_id="p",kind="fact",text="claim")

def test_memory_cannot_supersede_another_project():
 m=LongTermMemory();m.add(trusted("old","p1","A"))
 with pytest.raises(ValueError):m.add(trusted("new","p2","B","old"))

def test_planning_context_excludes_unverified_notes():
 m=LongTermMemory();m.add(MemoryItem(id="note",project_id="p",kind="note",text="unverified",verified=False))
 m.add(trusted("fact","p","verified"))
 ctx=ContextBuilder(m).build("p",{})
 assert [x["id"] for x in ctx["memories"]]==["fact"]
