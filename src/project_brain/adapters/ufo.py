from __future__ import annotations
from project_brain.contracts import ExecutionRequest, ExecutionResult

class UFOExecutorAdapter:
    """Boundary for UFO. No UFO source code is copied or modified here."""
    def __init__(self, transport) -> None:
        self.transport = transport

    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        payload = request.model_dump(mode="json")
        raw = await self.transport.execute(payload)
        return ExecutionResult.model_validate(raw)
