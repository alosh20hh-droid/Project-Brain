from __future__ import annotations
from datetime import datetime,timezone
from .types import ApprovalRequest,ApprovalStatus

class ApprovalStore:
 def __init__(self)->None:self._items:dict[str,ApprovalRequest]={}
 def create(self,item:ApprovalRequest)->None:
  if item.id in self._items:raise ValueError(f"duplicate approval: {item.id}")
  self._items[item.id]=item
 def get(self,item_id:str)->ApprovalRequest:return self._items[item_id]
 def decide(self,item_id:str,approved:bool,actor:str)->ApprovalRequest:
  item=self.get(item_id)
  if item.status!=ApprovalStatus.PENDING:raise ValueError("approval already decided")
  item.status=ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED
  item.decided_by=actor;item.decided_at=datetime.now(timezone.utc).isoformat()
  return item
