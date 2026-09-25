from __future__ import annotations
from project_brain.contracts import Executor, ExecutionRequest, ExecutionResult

class ExecutionRouter:
    def __init__(self) -> None:
        self._executors: dict[str, Executor] = {}

    def register(self, name: str, executor: Executor) -> None:
        self._executors[name] = executor

    async def execute(self, name: str, request: ExecutionRequest) -> ExecutionResult:
        if name not in self._executors:
            raise KeyError(f"Unknown executor: {name}")
        return await self._executors[name].execute(request)
