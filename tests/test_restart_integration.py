import asyncio
from project_brain.orchestrator import Orchestrator,OrchestratorConfig
from project_brain.bootstrap import bootstrap
from project_brain.cycle import CycleOutcome

class IdleCycle:
 async def run_once(self,state,executor_name):
  return CycleOutcome(state=state,request=None,result=None,verification=None,status="idle")

def test_new_process_style_bootstrap_loads_previous_state(tmp_path):
 db=tmp_path/"brain.db"
 first=bootstrap(db);first.projects.save_state("p",{"goal":"continue","step":7})
 second=bootstrap(db)
 cfg=OrchestratorConfig("p","restart","test",1)
 result=asyncio.run(Orchestrator(IdleCycle(),second.projects,second.runs,second.events,second.heartbeats,second.leases,cfg).run())
 assert result=={"goal":"continue","step":7}
