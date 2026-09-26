from .contracts import ExecutionRequest, RiskLevel

class ApprovalRequired(RuntimeError):
    pass

def require_owner_approval(request:ExecutionRequest,approved:bool=False)->None:
    if request.risk in {RiskLevel.SENSITIVE,RiskLevel.IRREVERSIBLE}:
        raise ApprovalRequired("Persisted scoped approval is required; boolean approval flags are not trusted")
