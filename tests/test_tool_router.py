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
 req=ExecutionRequest(task_id="t",goal="g",risk=RiskLevel.SENSITIVE,allowed_actions=["external"])
 assert asyncio.run(ToolRouter(reg,authorization=lambda request,call:True).execute(req,ToolCall("external",{"actions":["read"]}))).ok


def test_sensitive_tool_is_blocked_without_authorization_proof():
 reg=ToolRegistry();reg.register(ToolSpec(name="external",kind=ToolKind.EXTERNAL,description="external",allowed_actions=["read"]),external)
 req=ExecutionRequest(task_id="t",goal="g",risk=RiskLevel.SENSITIVE,allowed_actions=["external"])
 with pytest.raises(ToolAuthorizationError,match="authorization proof"):
  asyncio.run(ToolRouter(reg).execute(req,ToolCall("external",{"actions":["read"]})))

def test_sensitive_tool_rejects_invalid_authorization_proof():
 reg=ToolRegistry();reg.register(ToolSpec(name="external",kind=ToolKind.EXTERNAL,description="external",allowed_actions=["read"]),external)
 req=ExecutionRequest(task_id="t",goal="g",risk=RiskLevel.SENSITIVE,allowed_actions=["external"])
 with pytest.raises(ToolAuthorizationError,match="rejected"):
  asyncio.run(ToolRouter(reg,authorization=lambda request,call:False).execute(req,ToolCall("external",{"actions":["read"]})))
