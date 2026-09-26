from project_brain.persistence import SQLiteProjectStore,IdempotencyStore

def test_same_action_cannot_be_reserved_twice(tmp_path):
 i=IdempotencyStore(SQLiteProjectStore(tmp_path/"brain.db"))
 assert i.reserve("task:1")
 assert not i.reserve("task:1")
 i.complete("task:1","evidence:1")
 assert i.status("task:1")["status"]=="completed"


def test_second_store_cannot_reserve_same_action(tmp_path):
 db=tmp_path/"brain.db"
 first=IdempotencyStore(SQLiteProjectStore(db))
 second=IdempotencyStore(SQLiteProjectStore(db))
 assert first.reserve("same-action")
 assert not second.reserve("same-action")

import pytest

def test_unreserved_action_cannot_be_marked_completed(tmp_path):
 i=IdempotencyStore(SQLiteProjectStore(tmp_path/"brain.db"))
 with pytest.raises(RuntimeError):i.complete("never-reserved","result")

def test_completed_action_stays_completed_and_cannot_be_reserved_again(tmp_path):
 i=IdempotencyStore(SQLiteProjectStore(tmp_path/"brain.db"))
 assert i.reserve("pay:1");i.complete("pay:1","receipt:1")
 i.complete("pay:1","receipt:2")
 assert i.status("pay:1")["result_ref"]=="receipt:1"
 assert not i.reserve("pay:1")
