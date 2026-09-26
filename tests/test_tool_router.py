import asyncio,pytest
from project_brain.contracts import ExecutionRequest,RiskLevel
from project_brain.tools import ToolRegistry,ToolSpec,ToolKind,ToolResult,ToolRouter,ToolCall,ToolAuthorizationError

async def research(args):
    return ToolResult(ok=True,summary="researched",data=args)

def test_only_offered_tool_can_run():
    reg=ToolRegistry(); reg.register(ToolSpec(name="research",kind=ToolKind.RESEARCH,description="research"),research)
    router=ToolRouter(reg)
    req=ExecutionRequest(task_id="t",goal="g",allowed_actions=["research"])
    result=asyncio.run(router.execute(req,ToolCall("research",{"q":"x"})))
    assert result.ok

def test_unoffered_tool_is_hard_blocked():
    reg=ToolRegistry(); reg.register(ToolSpec(name="research",kind=ToolKind.RESEARCH,description="research"),research)
    router=ToolRouter(reg)
    req=ExecutionRequest(task_id="t",goal="g",allowed_actions=[])
    with pytest.raises(ToolAuthorizationError):
        asyncio.run(router.execute(req,ToolCall("research",{})))


async def external(args):
 return ToolResult(ok=True,summary="external",data=args)

def test_restricted_tool_requires_explicit_action():
 reg=ToolRegistry();reg.register(ToolSpec(name="external",kind=ToolKind.EXTERNAL,description="external",allowed_actions=["read"]),external)
 req=ExecutionRequest(task_id="t",goal="g",allowed_actions=["external"])
 with pytest.raises(ToolAuthorizationError):
  asyncio.run(ToolRouter(reg).execute(req,ToolCall("external",{})))

def test_restricted_tool_blocks_unapproved_action():
 reg=ToolRegistry();reg.register(ToolSpec(name="external",kind=ToolKind.EXTERNAL,description="external",allowed_actions=["read"]),external)
 req=ExecutionRequest(task_id="t",goal="g",allowed_actions=["external"])
 with pytest.raises(ToolAuthorizationError):
  asyncio.run(ToolRouter(reg).execute(req,ToolCall("external",{"actions":["delete"]})))


def test_external_tool_cannot_be_declared_low_risk_even_with_valid_action():
 reg=ToolRegistry();reg.register(ToolSpec(name="external",kind=ToolKind.EXTERNAL,description="external",allowed_actions=["read"]),external)
 req=ExecutionRequest(task_id="t",goal="g",risk=RiskLevel.LOW,allowed_actions=["external"])
 with pytest.raises(ToolAuthorizationError):asyncio.run(ToolRouter(reg).execute(req,ToolCall("external",{"actions":["read"]})))

def test_sensitive_external_tool_can_run_when_action_is_allowed():
 reg=ToolRegistry();reg.register(ToolSpec(name="external",kind=ToolKind.EXTERNAL,description="external",allowed_actions=["read"]),external)
 req=ExecutionRequest(task_id="t",goal="g",operation_id="op-t",risk=RiskLevel.SENSITIVE,allowed_actions=["external"])
 assert asyncio.run(ToolRouter(reg,authorization=lambda request,call:True).execute(req,ToolCall("external",{"actions":["read"]}))).ok


def test_sensitive_tool_is_blocked_without_authorization_proof():
 reg=ToolRegistry();reg.register(ToolSpec(name="external",kind=ToolKind.EXTERNAL,description="external",allowed_actions=["read"]),external)
 req=ExecutionRequest(task_id="t",goal="g",operation_id="op-t",risk=RiskLevel.SENSITIVE,allowed_actions=["external"])
 with pytest.raises(ToolAuthorizationError,match="authorization proof"):
  asyncio.run(ToolRouter(reg).execute(req,ToolCall("external",{"actions":["read"]})))

def test_sensitive_tool_rejects_invalid_authorization_proof():
 reg=ToolRegistry();reg.register(ToolSpec(name="external",kind=ToolKind.EXTERNAL,description="external",allowed_actions=["read"]),external)
 req=ExecutionRequest(task_id="t",goal="g",operation_id="op-t-rejected",risk=RiskLevel.SENSITIVE,allowed_actions=["external"])
 with pytest.raises(ToolAuthorizationError,match="authorization proof"):
  asyncio.run(ToolRouter(reg,authorization=lambda request,call:False).execute(req,ToolCall("external",{"actions":["read"]})))


def durable_router(tmp_path,record):
 from project_brain.persistence import SQLiteProjectStore,IdempotencyStore
 store=IdempotencyStore(SQLiteProjectStore(tmp_path/"brain.db"))
 store.reserve("op",record)
 reg=ToolRegistry();reg.register(ToolSpec(name="external",kind=ToolKind.EXTERNAL,description="external",allowed_actions=["read"]),external)
 return ToolRouter(reg,idempotency=store)

def sensitive_request(operation_id="op",task_id="t",goal="g"):
 return ExecutionRequest(task_id=task_id,goal=goal,operation_id=operation_id,risk=RiskLevel.SENSITIVE,allowed_actions=["external"])

def test_durable_authorization_allows_exact_reserved_operation(tmp_path):
 router=durable_router(tmp_path,{"task_id":"t","action":"g","approval_id":"approval-1"})
 assert asyncio.run(router.execute(sensitive_request(),ToolCall("external",{"actions":["read"]}))).ok

def test_durable_authorization_rejects_wrong_task(tmp_path):
 router=durable_router(tmp_path,{"task_id":"other","action":"g","approval_id":"approval-1"})
 with pytest.raises(ToolAuthorizationError):
  asyncio.run(router.execute(sensitive_request(),ToolCall("external",{"actions":["read"]})))

def test_durable_authorization_rejects_wrong_action(tmp_path):
 router=durable_router(tmp_path,{"task_id":"t","action":"other","approval_id":"approval-1"})
 with pytest.raises(ToolAuthorizationError):
  asyncio.run(router.execute(sensitive_request(),ToolCall("external",{"actions":["read"]})))

def test_durable_authorization_rejects_missing_approval(tmp_path):
 router=durable_router(tmp_path,{"task_id":"t","action":"g"})
 with pytest.raises(ToolAuthorizationError):
  asyncio.run(router.execute(sensitive_request(),ToolCall("external",{"actions":["read"]})))

def test_durable_authorization_rejects_wrong_operation_id(tmp_path):
 router=durable_router(tmp_path,{"task_id":"t","action":"g","approval_id":"approval-1"})
 with pytest.raises(ToolAuthorizationError):
  asyncio.run(router.execute(sensitive_request("different-op"),ToolCall("external",{"actions":["read"]})))

def test_completed_operation_cannot_authorize_sensitive_tool(tmp_path):
 from project_brain.persistence import SQLiteProjectStore,IdempotencyStore
 ids=IdempotencyStore(SQLiteProjectStore(tmp_path/"brain.db"));ids.reserve("op",{"task_id":"t","action":"g","approval_id":"approval-1"});ids.complete("op","done")
 reg=ToolRegistry();reg.register(ToolSpec(name="external",kind=ToolKind.EXTERNAL,description="external",allowed_actions=["read"]),external)
 with pytest.raises(ToolAuthorizationError):
  asyncio.run(ToolRouter(reg,idempotency=ids).execute(sensitive_request(),ToolCall("external",{"actions":["read"]})))
