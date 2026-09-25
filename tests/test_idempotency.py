from project_brain.persistence import SQLiteProjectStore,IdempotencyStore

def test_same_action_cannot_be_reserved_twice(tmp_path):
 i=IdempotencyStore(SQLiteProjectStore(tmp_path/"brain.db"))
 assert i.reserve("task:1")
 assert not i.reserve("task:1")
 i.complete("task:1","evidence:1")
 assert i.status("task:1")["status"]=="completed"
