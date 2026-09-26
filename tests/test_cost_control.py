from decimal import Decimal
import pytest
from project_brain.cost_control import CostLedger

def test_reservation_prevents_oversubscription():
 l=CostLedger(Decimal("10"))
 assert l.reserve(Decimal("7"))
 assert not l.reserve(Decimal("4"))

def test_settlement_moves_reserved_to_spent():
 l=CostLedger(Decimal("10"));l.reserve(Decimal("5"));l.settle(Decimal("5"),Decimal("4"))
 assert l.spent==Decimal("4");assert l.reserved==Decimal("0")


def test_failed_settlement_does_not_mutate_ledger():
 l=CostLedger(Decimal("10"));l.reserve(Decimal("5"))
 with pytest.raises(RuntimeError):l.settle(Decimal("5"),Decimal("11"))
 assert l.spent==Decimal("0")
 assert l.reserved==Decimal("5")


def test_persistent_budget_survives_restart_and_prevents_double_reserve(tmp_path):
 from project_brain.persistence import SQLiteProjectStore
 db=tmp_path/"brain.db"
 first=CostLedger(Decimal("10"),store=SQLiteProjectStore(db),ledger_id="project")
 second=CostLedger(Decimal("10"),store=SQLiteProjectStore(db),ledger_id="project")
 assert first.reserve(Decimal("7"))
 assert not second.reserve(Decimal("4"))
 restarted=CostLedger(Decimal("10"),store=SQLiteProjectStore(db),ledger_id="project")
 assert restarted.reserved==Decimal("7")
 assert restarted.available==Decimal("3")

def test_persistent_budget_settle_and_release_are_durable(tmp_path):
 from project_brain.persistence import SQLiteProjectStore
 db=tmp_path/"brain.db"
 ledger=CostLedger(Decimal("20"),store=SQLiteProjectStore(db),ledger_id="project")
 assert ledger.reserve(Decimal("10"))
 ledger.settle(Decimal("10"),Decimal("8"))
 assert ledger.spent==Decimal("8") and ledger.reserved==Decimal("0")
 assert ledger.reserve(Decimal("5"))
 ledger.release(Decimal("5"))
 restarted=CostLedger(Decimal("20"),store=SQLiteProjectStore(db),ledger_id="project")
 assert restarted.spent==Decimal("8")
 assert restarted.reserved==Decimal("0")
 assert restarted.available==Decimal("12")
