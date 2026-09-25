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
