from project_brain.long_term_memory import LongTermMemory,MemoryItem

def test_new_memory_can_supersede_old_memory():
 m=LongTermMemory()
 m.add(MemoryItem(id="old",project_id="p",kind="decision",text="A"))
 m.add(MemoryItem(id="new",project_id="p",kind="decision",text="B",supersedes="old"))
 ids=[x.id for x in m.query("p")]
 assert ids==["new"]

def test_projects_are_isolated():
 m=LongTermMemory()
 m.add(MemoryItem(id="a",project_id="p1",kind="fact",text="x"))
 m.add(MemoryItem(id="b",project_id="p2",kind="fact",text="y"))
 assert [x.id for x in m.query("p1")]==["a"]
