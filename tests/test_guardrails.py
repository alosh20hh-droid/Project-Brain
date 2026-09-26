from project_brain.contracts import ExecutionRequest,RiskLevel
from project_brain.guardrails import Guardrails

def test_irreversible_blocked_before_gateway():
    r=Guardrails().check(ExecutionRequest(task_id="x",goal="delete",operation_id="op-x",risk=RiskLevel.IRREVERSIBLE))
    assert not r.allowed
