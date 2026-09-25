from __future__ import annotations
from .provider import ModelProvider

class ModelRegistry:
    def __init__(self)->None:
        self._providers:dict[str,ModelProvider]={}

    def register(self,name:str,provider:ModelProvider)->None:
        if not name.strip(): raise ValueError("provider name is required")
        self._providers[name]=provider

    def get(self,name:str)->ModelProvider:
        if name not in self._providers: raise KeyError(f"Unknown model provider: {name}")
        return self._providers[name]
