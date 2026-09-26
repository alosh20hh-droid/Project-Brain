from project_brain.persistence import SQLiteProjectStore,RunStore,RunRecord
from project_brain.resume import ResumeManager

def test_resume_restores_state_and_run(tmp_path):
 p=tmp_path/"brain.db"; projects=SQLiteProjectStore(p); runs=RunStore(p)
 projects.save_state("p",{"phase":"verify"})
 runs.save(RunRecord("r","p","paused","task-7"))
 point=ResumeManager(projects,runs).load("p","r")
 assert point.state["phase"]=="verify"
 assert point.run.checkpoint=="task-7"


def test_resume_rejects_run_from_another_project(tmp_path):
 import pytest
 p=tmp_path/"brain.db";projects=SQLiteProjectStore(p);runs=RunStore(p)
 projects.save_state("p1",{"phase":"one"});projects.save_state("p2",{"phase":"two"})
 runs.save(RunRecord("r","p1","paused","task-7"))
 with pytest.raises(ValueError,match="different project"):
  ResumeManager(projects,runs).load("p2","r")
