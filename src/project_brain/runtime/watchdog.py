from __future__ import annotations
from dataclasses import dataclass,field
from .heartbeat import HeartbeatMonitor
from .leases import LeaseManager

@dataclass
class RecoveryReport:
 dead_workers:list[str]=field(default_factory=list)
 expired_tasks:list[str]=field(default_factory=list)

class Watchdog:
 def __init__(self,heartbeats:HeartbeatMonitor,leases:LeaseManager)->None:
  self.heartbeats=heartbeats;self.leases=leases
 def inspect(self,now=None)->RecoveryReport:
  return RecoveryReport(self.heartbeats.dead_workers(now),[x.task_id for x in self.leases.expired(now)])
