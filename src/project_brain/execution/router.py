from __future__ import annotations
import hashlib
import json
from project_brain.contracts import Executor,ExecutionRequest,ExecutionResult
from project_brain.persistence import IdempotencyStore

class ReconciliationRequired(RuntimeError):pass

def request_fingerprint(request:ExecutionRequest)->str:
 payload=request.model_dump(mode="json")
 raw=json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")
 return hashlib.sha256(raw).hexdigest()

class ExecutionRouter:
 def __init__(self,idempotency:IdempotencyStore|None=None)->None:
  self._executors:dict[str,Executor]={};self.idempotency=idempotency
 def register(self,name:str,executor:Executor)->None:
  if name in self._executors:raise ValueError(f"Executor already registered: {name}")
  self._executors[name]=executor
 async def _run(self,name:str,request:ExecutionRequest)->ExecutionResult:
  if name not in self._executors:raise KeyError(f"Unknown executor: {name}")
  result=await self._executors[name].execute(request)
  if result.task_id!=request.task_id:raise RuntimeError("executor returned a result for a different task")
  return result
 async def execute_reserved(self,name:str,request:ExecutionRequest)->ExecutionResult:
  if not self.idempotency:raise RuntimeError("idempotency store required for reserved execution")
  key=request.operation_id or request.task_id
  current=self.idempotency.status(key)
  if current is None or current.get("status")!="reserved":raise ReconciliationRequired(f"operation {key} is not reserved")
  if current.get("task_id") is not None and current.get("task_id")!=request.task_id:raise ReconciliationRequired(f"operation {key} belongs to a different task")
  if current.get("action") is not None and current.get("action")!=request.goal:raise ReconciliationRequired(f"operation {key} belongs to a different action")
  if current.get("request_fingerprint") is not None and current.get("request_fingerprint")!=request_fingerprint(request):
   raise ReconciliationRequired(f"operation {key} request changed after authorization")
  result=await self._run(name,request)
  self.idempotency.complete(key,result_ref=result.task_id)
  return result
 async def execute(self,name:str,request:ExecutionRequest)->ExecutionResult:
  key=request.operation_id or request.task_id
  if self.idempotency:
   current=self.idempotency.status(key)
   if current is not None:raise ReconciliationRequired(f"operation {key} was already reserved or completed")
   metadata={"task_id":request.task_id,"action":request.goal,"request_fingerprint":request_fingerprint(request)}
   if not self.idempotency.reserve(key,metadata):raise ReconciliationRequired(f"operation {key} was concurrently reserved")
  result=await self._run(name,request)
  if self.idempotency:self.idempotency.complete(key,result_ref=result.task_id)
  return result
