from __future__ import annotations
from dataclasses import dataclass
from project_brain.persistence import IdempotencyStore
from .watchdog import RecoveryReport

@dataclass(frozen=True)
class RecoveryAction:
 task_id:str
 action:str
 reason:str

class RecoveryCoordinator:
 def __init__(self,idempotency:IdempotencyStore)->None:self.idempotency=idempotency
 def plan(self,report:RecoveryReport)->list[RecoveryAction]:
  actions=[]
  for task_id in report.expired_tasks:
   status=self.idempotency.status(task_id)
   if status and status.get("status")=="completed":
    actions.append(RecoveryAction(task_id,"do_not_retry","already completed"))
   elif status and status.get("status")=="reserved":
    actions.append(RecoveryAction(task_id,"reconcile","execution state unknown"))
   else:
    actions.append(RecoveryAction(task_id,"requeue","safe to schedule again"))
  return actions
