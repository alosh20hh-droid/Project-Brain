from __future__ import annotations
import sqlite3
from dataclasses import dataclass
from datetime import datetime,timezone
from pathlib import Path

@dataclass(frozen=True)
class RunRecord:
 run_id:str; project_id:str; status:str; checkpoint:str|None=None

class RunStore:
 def __init__(self,path:str|Path)->None:
  self.path=str(path)
  with sqlite3.connect(self.path) as db:
   db.execute("CREATE TABLE IF NOT EXISTS runs(run_id TEXT PRIMARY KEY,project_id TEXT NOT NULL,status TEXT NOT NULL,checkpoint TEXT,updated_at TEXT NOT NULL)")
 def save(self,record:RunRecord)->None:
  now=datetime.now(timezone.utc).isoformat()
  with sqlite3.connect(self.path) as db:
   existing=db.execute("SELECT project_id FROM runs WHERE run_id=?",(record.run_id,)).fetchone()
   if existing is not None and existing[0]!=record.project_id:raise ValueError("run id belongs to a different project")
   db.execute("INSERT INTO runs(run_id,project_id,status,checkpoint,updated_at) VALUES(?,?,?,?,?) ON CONFLICT(run_id) DO UPDATE SET status=excluded.status,checkpoint=excluded.checkpoint,updated_at=excluded.updated_at",(record.run_id,record.project_id,record.status,record.checkpoint,now))
 def get(self,run_id:str)->RunRecord|None:
  with sqlite3.connect(self.path) as db:
   row=db.execute("SELECT run_id,project_id,status,checkpoint FROM runs WHERE run_id=?",(run_id,)).fetchone()
  return None if row is None else RunRecord(*row)
