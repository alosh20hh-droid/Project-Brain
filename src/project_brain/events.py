from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

@dataclass(frozen=True)
class Event:
    name: str
    payload: dict[str,Any]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class EventBus:
    def __init__(self) -> None:
        self._events: list[Event]=[]
    def publish(self,event: Event)->None:
        self._events.append(event)
    def all(self)->list[Event]:
        return list(self._events)
