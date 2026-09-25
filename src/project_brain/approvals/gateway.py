from __future__ import annotations
from dataclasses import dataclass
from .store import ApprovalStore
from .types import ApprovalStatus

@dataclass(frozen=True)
class ApprovalVerdict:
 allowed:bool
 reason:str

class ApprovalGateway:
 def __init__(self,store:ApprovalStore)->None:self.store=store
 def check(self,approval_id:str|None)->ApprovalVerdict:
  if not approval_id:return ApprovalVerdict(False,"explicit owner approval required")
  try:item=self.store.get(approval_id)
  except KeyError:return ApprovalVerdict(False,"approval not found")
  if item.status!=ApprovalStatus.APPROVED:return ApprovalVerdict(False,f"approval is {item.status.value}")
  return ApprovalVerdict(True,"approved")
