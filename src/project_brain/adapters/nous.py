from __future__ import annotations
from typing import Any

class NousBrainAdapter:
    """Boundary for Nous cognition/memory. Implementation is intentionally external."""
    def __init__(self, client: Any) -> None:
        self.client = client

    async def think(self, project_state: dict[str, Any]) -> dict[str, Any]:
        return await self.client.think(project_state)
