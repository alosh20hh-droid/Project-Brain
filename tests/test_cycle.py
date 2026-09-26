import asyncio
from project_brain.contracts import Evidence, EvidenceRequirement, ExecutionRequest, ExecutionResult
from project_brain.cycle import ProjectCycle
from project_brain.execution.router import ExecutionRouter
from project_brain.verifier import EvidenceVerifier
from project_brain.evidence.integrity import stable_hash

class Planner:
    async def next_request(self, state):
        return ExecutionRequest(task_id="x", goal="prove x", evidence_required=[EvidenceRequirement(kind="log", description="proof")])
    async def learn(self, state, request, result, verification):
        return {**state, "last_verified": verification.accepted}

class Executor:
    async def execute(self, request):
        return ExecutionResult(task_id=request.task_id, completed=True, summary="done", evidence=[Evidence(kind="log", source="test", content="ok", content_hash=stable_hash("ok"), strength="supporting")])

def test_full_cycle_accepts_verified_result():
    router=ExecutionRouter(); router.register("test", Executor())
    out=asyncio.run(ProjectCycle(Planner(), router, EvidenceVerifier()).run_once({}, "test"))
    assert out.status == "accepted"
    assert out.state["last_verified"] is True

from project_brain.contracts import RiskLevel
from project_brain.approval import ApprovalRequired
from project_brain.approvals import ApprovalStore,ApprovalRequest,ApprovalGateway
import pytest

class SensitivePlanner(Planner):
 async def next_request(self,state):
  return ExecutionRequest(task_id="s1",operation_id="op:s1:1",goal="sensitive-action",risk=RiskLevel.SENSITIVE)

def test_sensitive_cycle_requires_matching_persisted_approval():
 router=ExecutionRouter();router.register("test",Executor())
 store=ApprovalStore();gateway=ApprovalGateway(store)
 cycle=ProjectCycle(SensitivePlanner(),router,EvidenceVerifier(),gateway)
 with pytest.raises(ApprovalRequired):
  asyncio.run(cycle.run_once({},"test"))
 store.create(ApprovalRequest(id="a",task_id="other",operation_id="op:s1:1",action="sensitive-action",reason="test",risk="sensitive"))
 store.decide("a",True,"owner")
 with pytest.raises(ApprovalRequired):
  asyncio.run(cycle.run_once({},"test","a"))
 store.create(ApprovalRequest(id="b",task_id="s1",operation_id="op:s1:1",action="sensitive-action",reason="test",risk="sensitive"))
 store.decide("b",True,"owner")
 out=asyncio.run(cycle.run_once({},"test","b"))
 assert out.status=="accepted"


def test_sensitive_approval_cannot_authorize_different_operation():
 router=ExecutionRouter();router.register("test",Executor())
 store=ApprovalStore();gateway=ApprovalGateway(store);cycle=ProjectCycle(SensitivePlanner(),router,EvidenceVerifier(),gateway)
 store.create(ApprovalRequest(id="wrong-op",task_id="s1",operation_id="op:other",action="sensitive-action",reason="test",risk="sensitive"));store.decide("wrong-op",True,"owner")
 with pytest.raises(ApprovalRequired):asyncio.run(cycle.run_once({},"test","wrong-op"))

def test_sensitive_approval_is_consumed_after_one_execution():
 router=ExecutionRouter();router.register("test",Executor())
 store=ApprovalStore();gateway=ApprovalGateway(store);cycle=ProjectCycle(SensitivePlanner(),router,EvidenceVerifier(),gateway)
 store.create(ApprovalRequest(id="once",task_id="s1",operation_id="op:s1:1",action="sensitive-action",reason="test",risk="sensitive"));store.decide("once",True,"owner")
 asyncio.run(cycle.run_once({},"test","once"))
 with pytest.raises(ApprovalRequired):asyncio.run(cycle.run_once({},"test","once"))


def test_persistent_sensitive_cycle_atomically_consumes_and_reserves(tmp_path):
 from project_brain.persistence import SQLiteProjectStore,IdempotencyStore
 db=tmp_path/"brain.db";persistent=SQLiteProjectStore(db)
 router=ExecutionRouter(IdempotencyStore(persistent));router.register("test",Executor())
 store=ApprovalStore(persistent);gateway=ApprovalGateway(store)
 store.create(ApprovalRequest(id="atomic",task_id="s1",operation_id="op:s1:1",action="sensitive-action",reason="test",risk="sensitive"));store.decide("atomic",True,"owner")
 out=asyncio.run(ProjectCycle(SensitivePlanner(),router,EvidenceVerifier(),gateway).run_once({},"test","atomic"))
 assert out.status=="accepted"
 assert store.consumed("atomic")
 assert IdempotencyStore(persistent).status("op:s1:1")["status"]=="completed"


def test_sensitive_cycle_refuses_non_durable_authorization():
 from project_brain.approvals import ApprovalStore,ApprovalGateway,ApprovalRequest
 store=ApprovalStore();gateway=ApprovalGateway(store)
 store.create(ApprovalRequest(id="volatile",task_id="s1",operation_id="op:s1:1",action="sensitive-action",reason="test",risk="sensitive"));store.decide("volatile",True,"owner")
 router=ExecutionRouter();router.register("test",Executor())
 import pytest
 with pytest.raises(ApprovalRequired,match="durable"):
  asyncio.run(ProjectCycle(SensitivePlanner(),router,Verifier(),gateway).run_once({},"test","volatile"))

def test_atomic_sensitive_approval_cannot_be_rebound_to_other_task(tmp_path):
 from project_brain.persistence import SQLiteProjectStore,IdempotencyStore
 from project_brain.approvals import ApprovalStore,ApprovalGateway,ApprovalRequest
 persistent=SQLiteProjectStore(tmp_path/"scope.db");store=ApprovalStore(persistent);gateway=ApprovalGateway(store)
 store.create(ApprovalRequest(id="scope",task_id="s1",operation_id="op:s1:1",action="sensitive-action",reason="test",risk="sensitive"));store.decide("scope",True,"owner")
 verdict=gateway.reserve_operation("scope","op:s1:1",task_id="other",action="sensitive-action")
 assert verdict.allowed is False
 assert store.consumed("scope") is False
 assert IdempotencyStore(persistent).status("op:s1:1") is None
