import pytest
from project_brain.approval import ApprovalRequired, require_owner_approval
from project_brain.contracts import ExecutionRequest, RiskLevel

def test_sensitive_action_requires_approval():
    req = ExecutionRequest(task_id="pay", goal="pay", operation_id="op-pay", risk=RiskLevel.SENSITIVE)
    with pytest.raises(ApprovalRequired):
        require_owner_approval(req)

def test_low_risk_does_not_require_approval():
    req = ExecutionRequest(task_id="read", goal="read")
    require_owner_approval(req)


def test_boolean_true_cannot_bypass_sensitive_approval():
 req=ExecutionRequest(task_id="pay2",goal="pay",operation_id="op-pay2",risk=RiskLevel.SENSITIVE)
 with pytest.raises(ApprovalRequired):require_owner_approval(req,approved=True)
