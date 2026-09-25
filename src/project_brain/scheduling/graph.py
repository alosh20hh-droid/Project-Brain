from __future__ import annotations
from dataclasses import dataclass,field

@dataclass
class TaskNode:
 id:str
 dependencies:set[str]=field(default_factory=set)
 completed:bool=False
 failed:bool=False

class TaskGraph:
 def __init__(self)->None:self.nodes:dict[str,TaskNode]={}
 def add(self,node:TaskNode)->None:
  if node.id in self.nodes: raise ValueError(f"duplicate task: {node.id}")
  self.nodes[node.id]=node
 def validate(self)->None:
  for n in self.nodes.values():
   missing=n.dependencies-set(self.nodes)
   if missing: raise ValueError(f"missing dependencies for {n.id}: {sorted(missing)}")
  visiting=set(); visited=set()
  def walk(task_id:str):
   if task_id in visiting: raise ValueError("dependency cycle detected")
   if task_id in visited:return
   visiting.add(task_id)
   for dep in self.nodes[task_id].dependencies:walk(dep)
   visiting.remove(task_id);visited.add(task_id)
  for task_id in self.nodes:walk(task_id)
 def ready(self)->list[TaskNode]:
  self.validate()
  return [n for n in self.nodes.values() if not n.completed and not n.failed and all(self.nodes[d].completed for d in n.dependencies)]
