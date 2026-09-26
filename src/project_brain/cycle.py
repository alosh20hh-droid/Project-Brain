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
 def __init__(self,planner:BrainPlanner,router,verifier,approval_gateway=None)->None:
  self.planner=planner;self.router=router;self.verifier=verifier;self.approval_gateway=approval_gateway

 async def run_once(self,state:dict,executor_name:str,approval_id:str|None=None)->CycleOutcome:
  request=await self.planner.next_request(state)
  if request is None:return CycleOutcome(state,None,None,None,"idle")
  reserved_by_approval=False\n  if request.risk in {RiskLevel.SENSITIVE,RiskLevel.IRREVERSIBLE}:
   if self.approval_gateway is None:raise ApprovalRequired(f"Owner approval gateway required for task {request.task_id}")
   verdict=self.approval_gateway.check(approval_id,request.task_id,request.goal)
   if not verdict.allowed:raise ApprovalRequired(verdict.reason)
  result=await self.router.execute_reserved(executor_name,request) if reserved_by_approval else await self.router.execute(executor_name,request)
  verification=await self.verifier.verify(request,result)
  new_state=await self.planner.learn(state,request,result,verification)
  return CycleOutcome(new_state,request,result,verification,"accepted" if verification.accepted else "rejected")
