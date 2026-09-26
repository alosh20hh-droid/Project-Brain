from __future__ import annotations
from dataclasses import dataclass
from .persistence import SQLiteProjectStore,RunStore,RunRecord

@dataclass(frozen=True)
class ResumePoint:
 state:dict
 version:int
 run:RunRecord|None

class ResumeManager:
 def __init__(self,projects:SQLiteProjectStore,runs:RunStore)->None:
  self.projects=projects; self.runs=runs
 def load(self,project_id:str,run_id:str|None=None)->ResumePoint:
  state,version=self.projects.load_state(project_id)
  run=self.runs.get(run_id) if run_id else None
  if run is not None and run.project_id!=project_id:raise ValueError("run belongs to a different project")
  return ResumePoint(state,version,run)
