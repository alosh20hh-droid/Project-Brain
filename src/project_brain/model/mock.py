from __future__ import annotations
from .types import ModelResponse

class MockModelProvider:
    def __init__(self,responses:list[str])->None:
        self.responses=list(responses)
    async def complete(self,messages,tools=None)->ModelResponse:
        return ModelResponse(text=self.responses.pop(0) if self.responses else "")
