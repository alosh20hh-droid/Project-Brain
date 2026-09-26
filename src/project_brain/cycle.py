from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from .contracts import ExecutionRequest,ExecutionResult,VerificationResult,RiskLevel
from .approval import ApprovalRequired

class BrainPlanner(Protocol):
 async def next_request(self,state:dict)->ExecutionRequest|None:...
 async def learn(self,state:dict,request:ExecutionRequest,result:ExecutionResult,verification:VerificationResult)->dict:...

@dataclass
class CycleOutcome:
 state:dict
 request:ExecutionRequest|None
 result:ExecutionResult|None
 verification:VerificationResult|None
 status:str

class ProjectCycle:
 def __init__(self,planner:BrainPlanner,router,verifier,approval_gateway=None,guardrails=None)->None:
  self.planner=planner;self.router=router;self.verifier=verifier;self.approval_gateway=approval_gateway;self.guardrails=guardrails

 async def run_once(self,state:dict,executor_name:str,approval_id:str|None=None)->CycleOutcome:
  request=await self.planner.next_request(state)
  if request is None:return CycleOutcome(state,None,None,None,"idle")
  if self.guardrails is not None:
   guard=self.guardrails.check(request)
   if not guard.allowed and not (request.risk==RiskLevel.IRREVERSIBLE and self.approval_gateway is not None):raise ApprovalRequired(guard.reason)
  reserved_by_approval=False
  if request.risk in {RiskLevel.SENSITIVE,RiskLevel.IRREVERSIBLE}:
   if self.approval_gateway is None:raise ApprovalRequired(f"Owner approval gateway required for task {request.task_id}")
   if request.operation_id is None:raise ApprovalRequired("sensitive execution requires an operation id")
   if getattr(self.router,"idempotency",None) is None or self.approval_gateway.store.store is None:
    raise ApprovalRequired("sensitive execution requires durable approval and idempotency stores")
   reserved=self.approval_gateway.reserve_operation(approval_id,request.operation_id,task_id=request.task_id,action=request.goal)
   if not reserved.allowed:raise ApprovalRequired(reserved.reason)
   reserved_by_approval=True
  if reserved_by_approval:
   result=await self.router.execute_reserved(executor_name,request)
  else:
   result=await self.router.execute(executor_name,request)
  verification=await self.verifier.verify(request,result)
  new_state=await self.planner.learn(state,request,result,verification)
  return CycleOutcome(new_state,request,result,verification,"accepted" if verification.accepted else "rejected")
