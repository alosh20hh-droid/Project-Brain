from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field

class OutcomeMemory(BaseModel):
    task_id: str
    decision: str
    outcome: str
    accepted: bool
    lessons: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)

class MemoryStore:
    def __init__(self) -> None:
        self._items: list[OutcomeMemory] = []

    def add(self, item: OutcomeMemory) -> None:
        self._items.append(item)

    def all(self) -> list[OutcomeMemory]:
        return list(self._items)

    def failures(self) -> list[OutcomeMemory]:
        return [x for x in self._items if not x.accepted]
