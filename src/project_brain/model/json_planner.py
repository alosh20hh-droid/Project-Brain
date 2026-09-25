from __future__ import annotations
import json
from typing import Any
from .provider import ModelProvider,ModelProviderError
from .types import ModelMessage
from project_brain.contracts import ExecutionRequest

SYSTEM="""You are the planning brain of a long-running project.
Return JSON only. Choose the next bounded action that reduces uncertainty or advances a verified goal.
Never claim execution occurred. Never approve your own work.
Required keys: task_id, goal, hypothesis, constraints, allowed_actions, evidence_required, risk, timeout_seconds.
risk must be low, sensitive, or irreversible.
"""

class JsonModelPlanner:
    def __init__(self,provider:ModelProvider)->None:
        self.provider=provider

    async def next_request(self,state:dict[str,Any])->ExecutionRequest|None:
        response=await self.provider.complete([
            ModelMessage(role="system",content=SYSTEM),
            ModelMessage(role="user",content=json.dumps(state,ensure_ascii=False))
        ])
        if not response.text.strip(): return None
        try: data=json.loads(response.text)
        except json.JSONDecodeError as e: raise ModelProviderError("planner returned invalid JSON") from e
        if data.get("action")=="idle": return None
        return ExecutionRequest.model_validate(data)

    async def learn(self,state,request,result,verification):
        history=list(state.get("history",[]))
        history.append({"task_id":request.task_id,"goal":request.goal,"completed":result.completed,"verified":verification.accepted,"reasons":verification.reasons})
        return {**state,"history":history}
