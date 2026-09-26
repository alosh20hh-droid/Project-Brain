from __future__ import annotations
import asyncio,json
from typing import Any,Awaitable,Callable
from .provider import ModelProviderError
from .types import ModelMessage,ModelResponse

Transport=Callable[[dict[str,Any]],Awaitable[dict[str,Any]]]

class OpenAICompatibleProvider:
 """Provider-neutral adapter for OpenAI-compatible chat-completions transports.

 The transport owns HTTP/authentication. Project Brain only supplies validated
 messages/model settings, keeping secrets and vendor SDKs outside the core.
 """
 def __init__(self,transport:Transport,model:str,timeout_seconds:float=120)->None:
  if not model.strip():raise ValueError("model is required")
  self.transport=transport;self.model=model;self.timeout_seconds=timeout_seconds

 async def complete(self,messages:list[ModelMessage],tools:list[dict[str,Any]]|None=None)->ModelResponse:
  payload={"model":self.model,"messages":[m.model_dump() for m in messages]}
  if tools:payload["tools"]=tools
  try:
   raw=await asyncio.wait_for(self.transport(payload),timeout=self.timeout_seconds)
  except asyncio.TimeoutError as exc:raise ModelProviderError("model request timed out") from exc
  except Exception as exc:raise ModelProviderError("model transport failed") from exc
  try:
   choice=raw["choices"][0];message=choice["message"]
   text=message.get("content") or ""
   calls=[]
   for call in message.get("tool_calls") or []:
    fn=call.get("function") or {};args=fn.get("arguments") or {}
    if isinstance(args,str):args=json.loads(args)
    if not isinstance(args,dict):raise ValueError("tool arguments must be an object")
    calls.append({"id":call.get("id",""),"name":fn.get("name",""),"arguments":args})
   return ModelResponse(text=text,tool_calls=calls,usage=raw.get("usage") or {},raw=raw)
  except (KeyError,IndexError,TypeError,ValueError,json.JSONDecodeError) as exc:
   raise ModelProviderError("model returned an invalid response") from exc
