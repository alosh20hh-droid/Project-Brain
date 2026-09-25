from __future__ import annotations
from typing import Any

class PaperclipControlAdapter:
    """Boundary for project-control state and task lifecycle."""
    def __init__(self, client: Any) -> None:
        self.client = client

    async def publish_result(self, result: dict[str, Any]) -> Any:
        return await self.client.publish_result(result)
