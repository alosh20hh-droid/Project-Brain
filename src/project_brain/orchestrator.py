from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .cycle import ProjectCycle
from .approval import ApprovalRequired
from .execution.router import ReconciliationRequired
from .persistence import SQLiteProjectStore,RunStore,RunRecord
from .events import EventBus,Event
from .runtime import HeartbeatMonitor,LeaseManager,Watchdog

@dataclass
class OrchestratorConfig:
 project_id:str
 run_id:str
 executor_name:str
 max_cycles:int=50

class Orchestrator:
 def __init__(self,cycle:ProjectCycle,projects:SQLiteProjectStore,runs:RunStore,events:EventBus,heartbeats:HeartbeatMonitor,leases:LeaseManager,config:OrchestratorConfig)->None:
  self.cycle=cycle;self.projects=projects;self.runs=runs;self.events=events;self.heartbeats=heartbeats;self.leases=leases;self.config=config

 async def run(self,initial_state:dict[str,Any]|None=None,approval_id:str|None=None)->dict[str,Any]:
  state,version=self.projects.load_state(self.config.project_id)
  if not state:state=initial_state or {}
  self.runs.save(RunRecord(self.config.run_id,self.config.project_id,"running"))
  for index in range(self.config.max_cycles):
   self.events.publish(Event("orchestrator.cycle.started",{"run_id":self.config.run_id,"index":index}))
   try:outcome=await self.cycle.run_once(state,self.config.executor_name,approval_id)
   except ApprovalRequired as exc:
    self.runs.save(RunRecord(self.config.run_id,self.config.project_id,"blocked_approval",str(index)))
    self.events.publish(Event("orchestrator.blocked",{"run_id":self.config.run_id,"index":index,"reason":str(exc)}));return state
   except ReconciliationRequired as exc:
    self.runs.save(RunRecord(self.config.run_id,self.config.project_id,"blocked_reconciliation",str(index)))
    self.events.publish(Event("orchestrator.reconciliation_required",{"run_id":self.config.run_id,"index":index,"reason":str(exc)}));return state
   except Exception as exc:
    self.runs.save(RunRecord(self.config.run_id,self.config.project_id,"failed",str(index)))
    self.events.publish(Event("orchestrator.failed",{"run_id":self.config.run_id,"index":index,"error_type":type(exc).__name__}));raise
   state=outcome.state
   version=self.projects.save_state(self.config.project_id,state,expected_version=version)
   self.runs.save(RunRecord(self.config.run_id,self.config.project_id,outcome.status,str(index)))
   self.events.publish(Event("orchestrator.cycle.finished",{"run_id":self.config.run_id,"index":index,"status":outcome.status}))
   if outcome.status=="idle":break
  return state

 def health(self)->dict[str,Any]:
  report=Watchdog(self.heartbeats,self.leases).inspect()
  return {"dead_workers":report.dead_workers,"expired_tasks":report.expired_tasks}
