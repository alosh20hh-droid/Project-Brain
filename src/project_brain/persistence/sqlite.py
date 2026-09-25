from __future__ import annotations
import json,sqlite3
from pathlib import Path
from typing import Any

class SQLiteProjectStore:
 def __init__(self,path:str|Path)->None:
  self.path=str(path);self._init()
 def connect(self): return sqlite3.connect(self.path)
 def _init(self)->None:
  with self.connect() as db:
   db.execute("CREATE TABLE IF NOT EXISTS project_state(project_id TEXT PRIMARY KEY,state_json TEXT NOT NULL,version INTEGER NOT NULL DEFAULT 1)")
   db.execute("CREATE TABLE IF NOT EXISTS kv(namespace TEXT NOT NULL,key TEXT NOT NULL,value_json TEXT NOT NULL,PRIMARY KEY(namespace,key))")
 def save_state(self,project_id:str,state:dict[str,Any],expected_version:int|None=None)->int:
  raw=json.dumps(state,ensure_ascii=False,sort_keys=True)
  with self.connect() as db:
   row=db.execute("SELECT version FROM project_state WHERE project_id=?",(project_id,)).fetchone()
   if row is None:
    if expected_version not in (None,0): raise RuntimeError("state version conflict")
    db.execute("INSERT INTO project_state(project_id,state_json,version) VALUES(?,?,1)",(project_id,raw));return 1
   current=int(row[0])
   if expected_version is not None and expected_version!=current:raise RuntimeError("state version conflict")
   new=current+1
   db.execute("UPDATE project_state SET state_json=?,version=? WHERE project_id=?",(raw,new,project_id));return new
 def load_state(self,project_id:str)->tuple[dict[str,Any],int]:
  with self.connect() as db:row=db.execute("SELECT state_json,version FROM project_state WHERE project_id=?",(project_id,)).fetchone()
  return ({},0) if row is None else (json.loads(row[0]),int(row[1]))
 def put(self,namespace:str,key:str,value:Any)->None:
  raw=json.dumps(value,ensure_ascii=False,sort_keys=True)
  with self.connect() as db:db.execute("INSERT INTO kv(namespace,key,value_json) VALUES(?,?,?) ON CONFLICT(namespace,key) DO UPDATE SET value_json=excluded.value_json",(namespace,key,raw))
 def put_if_absent(self,namespace:str,key:str,value:Any)->bool:
  raw=json.dumps(value,ensure_ascii=False,sort_keys=True)
  with self.connect() as db:
   cur=db.execute("INSERT OR IGNORE INTO kv(namespace,key,value_json) VALUES(?,?,?)",(namespace,key,raw))
   return cur.rowcount==1
 def get(self,namespace:str,key:str,default:Any=None)->Any:
  with self.connect() as db:row=db.execute("SELECT value_json FROM kv WHERE namespace=? AND key=?",(namespace,key)).fetchone()
  return default if row is None else json.loads(row[0])
