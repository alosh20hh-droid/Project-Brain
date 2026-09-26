import pytest
from project_brain.approvals import ApprovalStore,ApprovalRequest,ApprovalGateway

def test_pending_approval_cannot_execute():
 s=ApprovalStore();s.create(ApprovalRequest(id="a",task_id="t",action="pay",reason="needed",risk="sensitive"))
 assert not ApprovalGateway(s).check("a").allowed

def test_only_explicit_decision_unlocks_action():
 s=ApprovalStore();s.create(ApprovalRequest(id="a",task_id="t",action="pay",reason="needed",risk="sensitive"))
 s.decide("a",True,"owner")
 assert ApprovalGateway(s).check("a").allowed
 with pytest.raises(ValueError):s.decide("a",True,"owner")


def test_approval_cannot_be_reused_for_another_task_or_action():
 s=ApprovalStore();s.create(ApprovalRequest(id="a",task_id="task-1",action="pay",reason="needed",risk="sensitive"))
 s.decide("a",True,"owner");g=ApprovalGateway(s)
 assert g.check("a","task-1","pay").allowed
 assert not g.check("a","task-2","pay").allowed
 assert not g.check("a","task-1","delete").allowed


def test_approval_and_consumption_survive_restart(tmp_path):
 from project_brain.persistence import SQLiteProjectStore
 db=tmp_path/"brain.db"
 first=ApprovalStore(SQLiteProjectStore(db));first.create(ApprovalRequest(id="persist",task_id="t",action="pay",reason="needed",risk="sensitive"));first.decide("persist",True,"owner")
 first_gateway=ApprovalGateway(first);assert first_gateway.check("persist","t","pay").allowed;assert first_gateway.consume("persist").allowed
 second=ApprovalGateway(ApprovalStore(SQLiteProjectStore(db)))
 assert not second.check("persist","t","pay").allowed


def test_expired_approval_is_blocked_and_persisted(tmp_path):
 from datetime import datetime,timezone,timedelta
 from project_brain.persistence import SQLiteProjectStore
 db=tmp_path/"brain.db";now=datetime.now(timezone.utc)
 s=ApprovalStore(SQLiteProjectStore(db));s.create(ApprovalRequest(id="old",task_id="t",action="pay",reason="needed",risk="sensitive",expires_at=(now-timedelta(seconds=1)).isoformat()));s.decide("old",True,"owner")
 assert not ApprovalGateway(s).check("old","t","pay",now=now).allowed
 restarted=ApprovalStore(SQLiteProjectStore(db))
 assert restarted.get("old").status.value=="expired"


def test_two_stores_cannot_consume_same_approval(tmp_path):
 from project_brain.persistence import SQLiteProjectStore
 db=tmp_path/"brain.db"
 first=ApprovalStore(SQLiteProjectStore(db));first.create(ApprovalRequest(id="shared",task_id="t",action="pay",reason="needed",risk="sensitive"));first.decide("shared",True,"owner")
 second=ApprovalStore(SQLiteProjectStore(db))
 assert first.consume("shared")
 assert not second.consume("shared")


def test_atomic_operation_reservation_rechecks_amount_and_currency(tmp_path):
 from decimal import Decimal
 from project_brain.persistence import SQLiteProjectStore
 db=tmp_path/"brain.db"
 store=ApprovalStore(SQLiteProjectStore(db))
 store.create(ApprovalRequest(id="money",task_id="t",action="buy",operation_id="op-money",reason="needed",risk="sensitive",amount=3,currency="USD"))
 store.decide("money",True,"owner")
 gateway=ApprovalGateway(store)
 assert not gateway.reserve_operation("money","op-money",task_id="t",action="buy",amount=Decimal("4"),currency="USD").allowed
 assert not gateway.reserve_operation("money","op-money",task_id="t",action="buy",amount=Decimal("3"),currency="EUR").allowed
 assert gateway.reserve_operation("money","op-money",task_id="t",action="buy",amount=Decimal("3"),currency="USD").allowed
 assert store.consumed("money")
