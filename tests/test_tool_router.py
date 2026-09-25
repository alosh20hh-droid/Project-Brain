import asyncio,pytest
from project_brain.contracts import ExecutionRequest
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
