from .contracts import ExecutionRequest, RiskLevel

class ApprovalRequired(RuntimeError):
    pass

def require_owner_approval(request: ExecutionRequest, approved: bool = False) -> None:
    if request.risk in {RiskLevel.SENSITIVE, RiskLevel.IRREVERSIBLE} and not approved:
        raise ApprovalRequired(f"Owner approval required for task {request.task_id}")
