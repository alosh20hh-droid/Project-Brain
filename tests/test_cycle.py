import asyncio
from project_brain.contracts import Evidence, EvidenceRequirement, ExecutionRequest, ExecutionResult
from project_brain.cycle import ProjectCycle
from project_brain.execution.router import ExecutionRouter
from project_brain.verifier import EvidenceVerifier

class Planner:
    async def next_request(self, state):
        return ExecutionRequest(task_id="x", goal="prove x", evidence_required=[EvidenceRequirement(kind="log", description="proof")])
    async def learn(self, state, request, result, verification):
        return {**state, "last_verified": verification.accepted}

class Executor:
    async def execute(self, request):
        return ExecutionResult(task_id=request.task_id, completed=True, summary="done", evidence=[Evidence(kind="log", source="test", content="ok")])

def test_full_cycle_accepts_verified_result():
    router=ExecutionRouter(); router.register("test", Executor())
    out=asyncio.run(ProjectCycle(Planner(), router, EvidenceVerifier()).run_once({}, "test"))
    assert out.status == "accepted"
    assert out.state["last_verified"] is True
