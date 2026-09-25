from __future__ import annotations
from dataclasses import dataclass
from .graph import TaskGraph
from .locks import LockManager

@dataclass(frozen=True)
class ScheduledTask:
 task_id:str
 resources:tuple[str,...]

class Scheduler:
 def __init__(self,graph:TaskGraph,locks:LockManager)->None:
  self.graph=graph;self.locks=locks
 def claim_ready(self,worker_id:str,resources_by_task:dict[str,list[str]],limit:int=1)->list[ScheduledTask]:
  claimed=[]
  for node in self.graph.ready():
   if not self.graph.claim(node.id,worker_id):continue
   resources=tuple(resources_by_task.get(node.id,[]));acquired=[]
   for resource in resources:
    if self.locks.acquire(resource,worker_id):acquired.append(resource)
    else:
     for r in acquired:self.locks.release(r,worker_id)
     self.graph.release_claim(node.id,worker_id)
     acquired=[];break
   if len(acquired)!=len(resources):continue
   claimed.append(ScheduledTask(node.id,resources))
   if len(claimed)>=limit:break
  return claimed
 def release(self,item:ScheduledTask,worker_id:str)->None:
  for resource in item.resources:self.locks.release(resource,worker_id)
  self.graph.release_claim(item.task_id,worker_id)
