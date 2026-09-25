import pytest
from project_brain.approval import ApprovalRequired, require_owner_approval
from project_brain.contracts import ExecutionRequest, RiskLevel

def test_sensitive_action_requires_approval():
    req = ExecutionRequest(task_id="pay", goal="pay", risk=RiskLevel.SENSITIVE)
    with pytest.raises(ApprovalRequired):
        require_owner_approval(req)

def test_low_risk_does_not_require_approval():
    req = ExecutionRequest(task_id="read", goal="read")
    require_owner_approval(req)
