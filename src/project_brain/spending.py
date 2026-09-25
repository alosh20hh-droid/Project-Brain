from __future__ import annotations
from decimal import Decimal
from dataclasses import dataclass
from .cost_control import CostLedger
from .approvals import ApprovalGateway

@dataclass(frozen=True)
class SpendVerdict:
 allowed:bool
 reason:str

class SpendingGate:
 def __init__(self,ledger:CostLedger,approvals:ApprovalGateway)->None:
  self.ledger=ledger;self.approvals=approvals
 def authorize(self,amount:Decimal,approval_id:str|None)->SpendVerdict:
  if amount<=0:return SpendVerdict(True,"no spend")
  verdict=self.approvals.check(approval_id)
  if not verdict.allowed:return SpendVerdict(False,verdict.reason)
  if not self.ledger.reserve(amount):return SpendVerdict(False,"budget unavailable")
  return SpendVerdict(True,"approved and reserved")
