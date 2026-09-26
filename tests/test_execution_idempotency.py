import asyncio,pytest
from project_brain.contracts import ExecutionRequest,ExecutionResult
from project_brain.execution.router import ExecutionRouter,ReconciliationRequired
from project_brain.persistence import SQLiteProjectStore,IdempotencyStore

class CrashingExecutor:
 def __init__(self):self.calls=0
 async def execute(self,request):
  self.calls+=1
  raise RuntimeError("crash after external side effect")

def test_crashed_external_operation_is_not_blindly_retried(tmp_path):
 store=IdempotencyStore(SQLiteProjectStore(tmp_path/"brain.db"));executor=CrashingExecutor()
 router=ExecutionRouter(store);router.register("external",executor)
 req=ExecutionRequest(task_id="t",operation_id="op:1",goal="external action")
 with pytest.raises(RuntimeError):asyncio.run(router.execute("external",req))
 restarted=ExecutionRouter(IdempotencyStore(SQLiteProjectStore(tmp_path/"brain.db")));restarted.register("external",executor)
 with pytest.raises(ReconciliationRequired):asyncio.run(restarted.execute("external",req))
 assert executor.calls==1
 assert store.status("op:1")["status"]=="reserved"

class SuccessfulExecutor:
 def __init__(self):self.calls=0
 async def execute(self,request):
  self.calls+=1;return ExecutionResult(task_id=request.task_id,completed=True,summary="done")

def test_completed_operation_cannot_execute_twice(tmp_path):
 store=IdempotencyStore(SQLiteProjectStore(tmp_path/"brain.db"));executor=SuccessfulExecutor()
 router=ExecutionRouter(store);router.register("external",executor)
 req=ExecutionRequest(task_id="t",operation_id="op:2",goal="external action")
 asyncio.run(router.execute("external",req))
 with pytest.raises(ReconciliationRequired):asyncio.run(router.execute("external",req))
 assert executor.calls==1
 assert store.status("op:2")["status"]=="completed"
