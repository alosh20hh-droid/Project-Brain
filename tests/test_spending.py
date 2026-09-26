from decimal import Decimal
from project_brain.cost_control import CostLedger
from project_brain.approvals import ApprovalStore,ApprovalRequest,ApprovalGateway
from project_brain.spending import SpendingGate

def test_money_requires_approval_and_budget():
 s=ApprovalStore();s.create(ApprovalRequest(id="a",task_id="t",action="buy",reason="test",risk="sensitive",amount=3,currency="USD"))
 gate=SpendingGate(CostLedger(Decimal("10")),ApprovalGateway(s))
 assert not gate.authorize(Decimal("3"),"a",task_id="t",action="buy",currency="USD").allowed
 s.decide("a",True,"owner")
 assert gate.authorize(Decimal("3"),"a",task_id="t",action="buy",currency="USD").allowed

def test_small_approval_cannot_authorize_larger_or_other_currency():
 s=ApprovalStore();s.create(ApprovalRequest(id="a",task_id="t",action="buy",reason="test",risk="sensitive",amount=3,currency="USD"));s.decide("a",True,"owner")
 gate=SpendingGate(CostLedger(Decimal("100")),ApprovalGateway(s))
 assert not gate.authorize(Decimal("100"),"a",task_id="t",action="buy",currency="USD").allowed
 assert not gate.authorize(Decimal("3"),"a",task_id="t",action="buy",currency="EUR").allowed


def test_approved_spend_token_cannot_be_used_twice():
 s=ApprovalStore();s.create(ApprovalRequest(id="one",task_id="t",action="buy",reason="test",risk="sensitive",amount=3,currency="USD"));s.decide("one",True,"owner")
 gate=SpendingGate(CostLedger(Decimal("100")),ApprovalGateway(s))
 first=gate.authorize(Decimal("3"),"one",task_id="t",action="buy",currency="USD")
 second=gate.authorize(Decimal("3"),"one",task_id="t",action="buy",currency="USD")
 assert first.allowed
 assert not second.allowed


def test_naive_expiry_is_handled_as_utc_not_crash():
 from datetime import datetime,timedelta,timezone
 s=ApprovalStore()
 expired=(datetime.now(timezone.utc)-timedelta(minutes=1)).replace(tzinfo=None).isoformat()
 s.create(ApprovalRequest(id="expired",task_id="t",action="buy",reason="test",risk="sensitive",amount=1,currency="USD",expires_at=expired))
 s.decide("expired",True,"owner")
 verdict=SpendingGate(CostLedger(Decimal("10")),ApprovalGateway(s)).authorize(Decimal("1"),"expired",task_id="t",action="buy",currency="USD")
 assert not verdict.allowed
 assert verdict.reason=="approval expired"
