from __future__ import annotations
from typing import Any, Protocol
from .types import ModelMessage, ModelResponse

class ModelProvider(Protocol):
    async def complete(self,messages:list[ModelMessage],tools:list[dict[str,Any]]|None=None)->ModelResponse: ...

class ModelProviderError(RuntimeError):
    pass
