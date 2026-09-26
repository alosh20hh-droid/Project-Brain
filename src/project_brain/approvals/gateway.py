from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from .store import ApprovalStore
from .types import ApprovalStatus

@dataclass(frozen=True)
class ApprovalVerdict:
 allowed:bool
 reason:str

class ApprovalGateway:
 def __init__(self,store:ApprovalStore)->None:self.store=store
 def check(self,approval_id:str|None,task_id:str|None=None,action:str|None=None,amount:Decimal|None=None,currency:str|None=None)->ApprovalVerdict:
  if not approval_id:return ApprovalVerdict(False,"explicit owner approval required")
  try:item=self.store.get(approval_id)
  except KeyError:return ApprovalVerdict(False,"approval not found")
  if item.status!=ApprovalStatus.APPROVED:return ApprovalVerdict(False,f"approval is {item.status.value}")
  if task_id is not None and item.task_id!=task_id:return ApprovalVerdict(False,"approval belongs to a different task")
  if action is not None and item.action!=action:return ApprovalVerdict(False,"approval belongs to a different action")
  if amount is not None:
   if item.amount is None:return ApprovalVerdict(False,"approval has no spending amount")
   if amount>Decimal(str(item.amount)):return ApprovalVerdict(False,"amount exceeds approved limit")
  if currency is not None:
   if item.currency is None or item.currency.upper()!=currency.upper():return ApprovalVerdict(False,"currency differs from approval")
  if self.store.consumed(approval_id):return ApprovalVerdict(False,"approval already consumed")\n  return ApprovalVerdict(True,"approved")

 def consume(self,approval_id:str)->ApprovalVerdict:
  try:ok=self.store.consume(approval_id)
  except KeyError:return ApprovalVerdict(False,"approval not found")
  return ApprovalVerdict(ok,"consumed" if ok else "approval cannot be consumed")
