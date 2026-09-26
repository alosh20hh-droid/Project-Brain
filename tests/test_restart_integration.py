import asyncio
from project_brain.orchestrator import Orchestrator,OrchestratorConfig
from project_brain.bootstrap import bootstrap
from project_brain.cycle import CycleOutcome

class IdleCycle:
 async def run_once(self,state,executor_name,approval_id=None):
  return CycleOutcome(state=state,request=None,result=None,verification=None,status="idle")

def test_new_process_style_bootstrap_loads_previous_state(tmp_path):
 db=tmp_path/"brain.db"
 first=bootstrap(db);first.projects.save_state("p",{"goal":"continue","step":7})
 second=bootstrap(db)
 cfg=OrchestratorConfig("p","restart","test",1)
 result=asyncio.run(Orchestrator(IdleCycle(),second.projects,second.runs,second.events,second.heartbeats,second.leases,cfg).run())
 assert result=={"goal":"continue","step":7}

from datetime import datetime,timezone,timedelta

def test_restart_preserves_worker_and_task_safety_state(tmp_path):
 db=tmp_path/"brain.db";now=datetime.now(timezone.utc)
 first=bootstrap(db);first.heartbeats.beat("worker-1",now);assert first.leases.claim("task-1","worker-1",30,now)
 second=bootstrap(db)
 assert second.heartbeats.alive("worker-1",now+timedelta(seconds=10))
 assert not second.leases.claim("task-1","worker-2",30,now+timedelta(seconds=10))
 assert second.leases.claim("task-1","worker-2",30,now+timedelta(seconds=31))
