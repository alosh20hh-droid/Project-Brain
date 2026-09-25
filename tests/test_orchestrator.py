import asyncio
from project_brain.orchestrator import Orchestrator,OrchestratorConfig
from project_brain.bootstrap import bootstrap
from project_brain.cycle import CycleOutcome

class OneShotCycle:
 def __init__(self):self.calls=0
 async def run_once(self,state,executor_name):
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
