from __future__ import annotations
from pathlib import Path
from .persistence import SQLiteProjectStore,RunStore,IdempotencyStore
from .events import EventBus
from .runtime import HeartbeatMonitor,LeaseManager
from .approvals import ApprovalStore,ApprovalGateway
from .execution.router import ExecutionRouter
from .evidence import EvidenceStore
from .long_term_memory import LongTermMemory

class RuntimeServices:
 def __init__(self,db_path:str|Path)->None:
  self.projects=SQLiteProjectStore(db_path)
  self.runs=RunStore(db_path)
  self.events=EventBus()
  self.idempotency=IdempotencyStore(self.projects)
  self.approval_store=ApprovalStore(self.projects)
  self.approvals=ApprovalGateway(self.approval_store)
  self.execution=ExecutionRouter(self.idempotency)
  self.evidence=EvidenceStore()
  self.memory=LongTermMemory()
  self.heartbeats=HeartbeatMonitor(store=self.projects)
  self.leases=LeaseManager(store=self.projects)

def bootstrap(db_path:str|Path)->RuntimeServices:return RuntimeServices(db_path)
