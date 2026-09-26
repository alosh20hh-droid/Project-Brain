from __future__ import annotations
import json
from typing import Any
from .provider import ModelProvider,ModelProviderError
from .types import ModelMessage
from project_brain.contracts import ExecutionRequest
from pydantic import ValidationError

SENSITIVE_KEYS={"password","passwd","secret","token","api_key","apikey","authorization","cookie","private_key"}

def _safe_context(value:Any,depth:int=0)->Any:
    if depth>8:return "[truncated]"
    if isinstance(value,dict):return {str(k):("[redacted]" if str(k).lower() in SENSITIVE_KEYS else _safe_context(v,depth+1)) for k,v in value.items()}
    if isinstance(value,list):return [_safe_context(v,depth+1) for v in value[-100:]]
    if isinstance(value,str) and len(value)>4000:return value[:4000]+"...[truncated]"
    return value

SYSTEM="""You are the planning brain of a long-running project.
Return JSON only. Choose the next bounded action that reduces uncertainty or advances a verified goal.
Never claim execution occurred. Never approve your own work.
Required keys: task_id, goal, hypothesis, constraints, allowed_actions, evidence_required, risk, timeout_seconds.\nFor sensitive or irreversible actions, operation_id is mandatory and must be stable for that exact operation.
risk must be low, sensitive, or irreversible.
"""

class JsonModelPlanner:
    def __init__(self,provider:ModelProvider)->None:
        self.provider=provider

    async def next_request(self,state:dict[str,Any])->ExecutionRequest|None:
        response=await self.provider.complete([
            ModelMessage(role="system",content=SYSTEM),
            ModelMessage(role="user",content=json.dumps(_safe_context(state),ensure_ascii=False)[:50000])
        ])
        if not response.text.strip(): return None
        try: data=json.loads(response.text)
        except json.JSONDecodeError as e: raise ModelProviderError("planner returned invalid JSON") from e
        if data.get("action")=="idle": return None
        try: return ExecutionRequest.model_validate(data)
        except ValidationError as e: raise ModelProviderError("planner returned an invalid execution request") from e

    async def learn(self,state,request,result,verification):
        history=list(state.get("history",[]))[-99:]
        history.append({"task_id":request.task_id,"goal":request.goal,"completed":result.completed,"verified":verification.accepted,"reasons":verification.reasons})
        return {**state,"history":history}
