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


def test_crashed_side_effect_remains_reconciliation_only_after_restart(tmp_path):
 db=tmp_path/"restart-crash.db"
 first=IdempotencyStore(SQLiteProjectStore(db))
 assert first.reserve("op-crash",{"task_id":"task-crash","action":"charge"})
 restarted=IdempotencyStore(SQLiteProjectStore(db))
 action=RecoveryCoordinator(restarted).plan(RecoveryReport(expired_tasks=["op-crash"]))[0]
 assert action.action=="reconcile"
 assert action.reason=="execution state unknown"

def test_operation_with_no_reservation_can_be_requeued(tmp_path):
 i=IdempotencyStore(SQLiteProjectStore(tmp_path/"clean.db"))
 action=RecoveryCoordinator(i).plan(RecoveryReport(expired_tasks=["never-started"]))[0]
 assert action.action=="requeue"
