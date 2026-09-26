import asyncio
from project_brain.orchestrator import Orchestrator,OrchestratorConfig
from project_brain.bootstrap import bootstrap
from project_brain.cycle import CycleOutcome

class OneShotCycle:
 def __init__(self):self.calls=0
 async def run_once(self,state,executor_name,approval_id=None):
  self.calls+=1
  if self.calls==1:
   return CycleOutcome(state={**state,"count":state.get("count",0)+1},request=None,result=None,verification=None,status="accepted")
  return CycleOutcome(state=state,request=None,result=None,verification=None,status="idle")

def test_end_to_end_state_is_persisted_and_resumable(tmp_path):
 db=tmp_path/"brain.db";services=bootstrap(db);cycle=OneShotCycle()
 cfg=OrchestratorConfig(project_id="p",run_id="r1",executor_name="test",max_cycles=3)
 state=asyncio.run(Orchestrator(cycle,services.projects,services.runs,services.events,services.heartbeats,services.leases,cfg).run({"count":0}))
 assert state["count"]==1
 saved,version=services.projects.load_state("p")
 assert saved["count"]==1 and version==2
 assert services.runs.get("r1").status=="idle"


class BlockedCycle:
 async def run_once(self,state,executor_name,approval_id=None):
  from project_brain.approval import ApprovalRequired
  raise ApprovalRequired("owner approval required")

def test_approval_block_is_persisted_instead_of_leaving_run_running(tmp_path):
 db=tmp_path/"blocked.db";services=bootstrap(db)
 cfg=OrchestratorConfig(project_id="p",run_id="blocked",executor_name="test")
 state=asyncio.run(Orchestrator(BlockedCycle(),services.projects,services.runs,services.events,services.heartbeats,services.leases,cfg).run({"safe":True}))
 assert state["safe"] is True
 assert services.runs.get("blocked").status=="blocked_approval"


class AlwaysActiveCycle:
 async def run_once(self,state,executor_name,approval_id=None):
  return CycleOutcome(state={**state,"ticks":state.get("ticks",0)+1},request=None,result=None,verification=None,status="accepted")

def test_cycle_limit_is_explicitly_persisted(tmp_path):
 db=tmp_path/"limit.db";services=bootstrap(db)
 cfg=OrchestratorConfig(project_id="p",run_id="limit",executor_name="test",max_cycles=2)
 state=asyncio.run(Orchestrator(AlwaysActiveCycle(),services.projects,services.runs,services.events,services.heartbeats,services.leases,cfg).run({"ticks":0}))
 assert state["ticks"]==2
 assert services.runs.get("limit").status=="cycle_limit"

def test_run_id_cannot_be_reused_for_another_project(tmp_path):
 db=tmp_path/"runs.db";services=bootstrap(db)
 first=OrchestratorConfig(project_id="p1",run_id="same",executor_name="test",max_cycles=1)
 asyncio.run(Orchestrator(AlwaysActiveCycle(),services.projects,services.runs,services.events,services.heartbeats,services.leases,first).run({}))
 second=OrchestratorConfig(project_id="p2",run_id="same",executor_name="test",max_cycles=1)
 import pytest
 with pytest.raises(ValueError,match="different project"):
  asyncio.run(Orchestrator(AlwaysActiveCycle(),services.projects,services.runs,services.events,services.heartbeats,services.leases,second).run({}))


def test_state_persistence_failure_never_leaves_run_running(tmp_path):
 db=tmp_path/"persist-fail.db";services=bootstrap(db)
 cfg=OrchestratorConfig(project_id="p",run_id="persist-fail",executor_name="test",max_cycles=1)
 original=services.projects.save_state
 def fail_save(*args,**kwargs):raise RuntimeError("disk write failed")
 services.projects.save_state=fail_save
 import pytest
 with pytest.raises(RuntimeError,match="disk write failed"):
  asyncio.run(Orchestrator(AlwaysActiveCycle(),services.projects,services.runs,services.events,services.heartbeats,services.leases,cfg).run({}))
 assert services.runs.get("persist-fail").status=="failed_persistence"
 services.projects.save_state=original
