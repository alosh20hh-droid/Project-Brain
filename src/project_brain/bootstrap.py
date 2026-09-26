from __future__ import annotations
from pathlib import Path
from .persistence import SQLiteProjectStore,RunStore
from .events import EventBus
from .runtime import HeartbeatMonitor,LeaseManager

class RuntimeServices:
 def __init__(self,db_path:str|Path)->None:
  self.projects=SQLiteProjectStore(db_path);self.runs=RunStore(db_path);self.events=EventBus()
  self.heartbeats=HeartbeatMonitor(store=self.projects);self.leases=LeaseManager(store=self.projects)

def bootstrap(db_path:str|Path)->RuntimeServices:return RuntimeServices(db_path)
