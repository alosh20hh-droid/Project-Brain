from __future__ import annotations
from project_brain.contracts import Executor,ExecutionRequest,ExecutionResult

class ExecutionRouter:
 def __init__(self)->None:self._executors:dict[str,Executor]={}
 def register(self,name:str,executor:Executor)->None:
  if name in self._executors:raise ValueError(f"Executor already registered: {name}")
  self._executors[name]=executor
 async def execute(self,name:str,request:ExecutionRequest)->ExecutionResult:
  if name not in self._executors:raise KeyError(f"Unknown executor: {name}")
  result=await self._executors[name].execute(request)
  if result.task_id!=request.task_id:
   raise RuntimeError("executor returned a result for a different task")
  return result
