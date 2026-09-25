from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .cycle import ProjectCycle, CycleOutcome
from .checkpoint import JsonCheckpointStore
from .events import Event, EventBus

@dataclass
class EngineConfig:
    executor_name: str
    max_cycles: int = 50

class BrainEngine:
    def __init__(self, cycle: ProjectCycle, checkpoint: JsonCheckpointStore, events: EventBus, config: EngineConfig):
        self.cycle=cycle; self.checkpoint=checkpoint; self.events=events; self.config=config

    async def run(self, initial_state: dict[str,Any] | None=None) -> dict[str,Any]:
        state=self.checkpoint.load() or (initial_state or {})
        for index in range(self.config.max_cycles):
            self.events.publish(Event("cycle.started",{"index":index}))
            outcome: CycleOutcome=await self.cycle.run_once(state,self.config.executor_name)
            state=outcome.state
            self.checkpoint.save(state)
            self.events.publish(Event("cycle.finished",{"index":index,"status":outcome.status}))
            if outcome.status=="idle":
                break
        return state
