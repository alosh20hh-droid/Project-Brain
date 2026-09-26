from __future__ import annotations
from enum import Enum
from datetime import datetime,timezone
from pydantic import BaseModel,Field

class ApprovalStatus(str,Enum):
 PENDING="pending"; APPROVED="approved"; REJECTED="rejected"; EXPIRED="expired"

class ApprovalRequest(BaseModel):
 id:str
 task_id:str
 action:str
 operation_id:str|None=None
 reason:str
 risk:str
 amount:float|None=None
 currency:str|None=None
 status:ApprovalStatus=ApprovalStatus.PENDING
 created_at:str=Field(default_factory=lambda:datetime.now(timezone.utc).isoformat())
 decided_at:str|None=None
 decided_by:str|None=None
 expires_at:str|None=None
