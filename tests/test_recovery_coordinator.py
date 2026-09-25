from project_brain.persistence import SQLiteProjectStore,IdempotencyStore
from project_brain.runtime import RecoveryCoordinator,RecoveryReport

def test_unknown_reserved_execution_is_reconciled_not_retried(tmp_path):
 i=IdempotencyStore(SQLiteProjectStore(tmp_path/"brain.db"));i.reserve("t")
 actions=RecoveryCoordinator(i).plan(RecoveryReport(expired_tasks=["t"]))
 assert actions[0].action=="reconcile"

def test_completed_execution_is_never_retried(tmp_path):
 i=IdempotencyStore(SQLiteProjectStore(tmp_path/"brain.db"));i.reserve("t");i.complete("t","e1")
 actions=RecoveryCoordinator(i).plan(RecoveryReport(expired_tasks=["t"]))
 assert actions[0].action=="do_not_retry"
