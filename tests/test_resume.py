from project_brain.persistence import SQLiteProjectStore,RunStore,RunRecord
from project_brain.resume import ResumeManager

def test_resume_restores_state_and_run(tmp_path):
 p=tmp_path/"brain.db"; projects=SQLiteProjectStore(p); runs=RunStore(p)
 projects.save_state("p",{"phase":"verify"})
 runs.save(RunRecord("r","p","paused","task-7"))
 point=ResumeManager(projects,runs).load("p","r")
 assert point.state["phase"]=="verify"
 assert point.run.checkpoint=="task-7"
