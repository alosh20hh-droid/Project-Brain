import asyncio,json
from project_brain.bootstrap import bootstrap
from project_brain.contracts import Evidence,ExecutionResult
from project_brain.cycle import ProjectCycle
from project_brain.model.json_planner import JsonModelPlanner
from project_brain.model.mock import MockModelProvider
from project_brain.orchestrator import Orchestrator,OrchestratorConfig
from project_brain.verifier import EvidenceVerifier
from project_brain.evidence.integrity import stable_hash

class JourneyExecutor:
 def __init__(self):self.calls=0
 async def execute(self,request):
  self.calls+=1
  value="bad" if self.calls==1 else "good"
  return ExecutionResult(task_id=request.task_id,completed=True,summary=value,evidence=[Evidence(kind="proof",source="journey",content=value,content_hash=stable_hash(value),strength="weak" if value=="bad" else "strong")])

def request(task_id):
 return json.dumps({"task_id":task_id,"goal":"prove the project step","hypothesis":"the second attempt can repair a rejected result","constraints":[],"allowed_actions":["test"],"evidence_required":[{"kind":"proof","description":"independent proof"}],"risk":"low","timeout_seconds":60})

def test_full_journey_rejects_repairs_persists_and_resumes(tmp_path):
 db=tmp_path/"journey.db";services=bootstrap(db)
 planner=JsonModelPlanner(MockModelProvider([request("attempt-1"),request("attempt-2"),""]))
 executor=JourneyExecutor();services.execution.register("journey",executor)
 cycle=ProjectCycle(planner,services.execution,EvidenceVerifier(),services.approvals)
 cfg=OrchestratorConfig(project_id="journey-project",run_id="journey-run",executor_name="journey",max_cycles=5)
 state=asyncio.run(Orchestrator(cycle,services.projects,services.runs,services.events,services.heartbeats,services.leases,cfg).run({"goal":"finish safely"}))
 assert [x["verified"] for x in state["history"]]==[False,True]
 assert executor.calls==2
 assert services.runs.get("journey-run").status=="idle"
 restarted=bootstrap(db)
 saved,version=restarted.projects.load_state("journey-project")
 assert saved["history"]==state["history"] and version>=2
 assert restarted.runs.get("journey-run").status=="idle"
