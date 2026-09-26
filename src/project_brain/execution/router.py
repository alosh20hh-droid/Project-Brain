from __future__ import annotations
from project_brain.contracts import Executor,ExecutionRequest,ExecutionResult
from project_brain.persistence import IdempotencyStore

class ReconciliationRequired(RuntimeError):pass

class ExecutionRouter:
 def __init__(self,idempotency:IdempotencyStore|None=None)->None:self._executors:dict[str,Executor]={};self.idempotency=idempotency
 def register(self,name:str,executor:Executor)->None:
  if name in self._executors:raise ValueError(f"Executor already registered: {name}")
  self._executors[name]=executor
 async def execute(self,name:str,request:ExecutionRequest)->ExecutionResult:
  if name not in self._executors:raise KeyError(f"Unknown executor: {name}")
  key=request.operation_id or request.task_id
  if self.idempotency:
   current=self.idempotency.status(key)
   if current is not None:raise ReconciliationRequired(f"operation {key} was already reserved or completed")
   if not self.idempotency.reserve(key):raise ReconciliationRequired(f"operation {key} was concurrently reserved")
  result=await self._executors[name].execute(request)
  if result.task_id!=request.task_id:raise RuntimeError("executor returned a result for a different task")
  if self.idempotency:self.idempotency.complete(key,result_ref=result.task_id)
  return result
