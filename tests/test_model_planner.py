import asyncio,json
from project_brain.model.mock import MockModelProvider
from project_brain.model.json_planner import JsonModelPlanner

def test_model_can_create_bounded_request():
    payload={"task_id":"t1","goal":"verify assumption","hypothesis":"x","constraints":["no spending"],"allowed_actions":["research"],"evidence_required":[{"kind":"source","description":"primary source"}],"risk":"low","timeout_seconds":60}
    planner=JsonModelPlanner(MockModelProvider([json.dumps(payload)]))
    req=asyncio.run(planner.next_request({"goal":"test"}))
    assert req.task_id=="t1"
    assert req.allowed_actions==["research"]

def test_empty_model_response_means_idle():
    planner=JsonModelPlanner(MockModelProvider([""]))
    assert asyncio.run(planner.next_request({})) is None


def test_invalid_request_is_wrapped_as_provider_error():
 from project_brain.model import ModelProviderError
 import pytest
 planner=JsonModelPlanner(MockModelProvider(['{"goal":"missing task"}']))
 with pytest.raises(ModelProviderError,match="invalid execution request"):
  asyncio.run(planner.next_request({}))

def test_history_is_bounded_for_long_running_projects():
 planner=JsonModelPlanner(MockModelProvider([]))
 from project_brain.contracts import ExecutionRequest,ExecutionResult,VerificationResult
 state={"history":[{"task_id":str(i)} for i in range(150)]}
 out=asyncio.run(planner.learn(state,ExecutionRequest(task_id="new",goal="g"),ExecutionResult(task_id="new",completed=True,summary="ok"),VerificationResult(task_id="new",accepted=True)))
 assert len(out["history"])==100
 assert out["history"][-1]["task_id"]=="new"


def test_planner_redacts_secrets_before_model_call():
 from project_brain.model.types import ModelResponse
 class Capture:
  def __init__(self):self.messages=None
  async def complete(self,messages,tools=None):
   self.messages=messages;return ModelResponse(text="")
 provider=Capture();planner=JsonModelPlanner(provider)
 asyncio.run(planner.next_request({"goal":"x","api_key":"super-secret","nested":{"token":"hidden","safe":"visible"}}))
 prompt=provider.messages[1].content
 assert "super-secret" not in prompt and "hidden" not in prompt
 assert "[redacted]" in prompt and "visible" in prompt

def test_planner_context_is_bounded():
 from project_brain.model.types import ModelResponse
 class Capture:
  def __init__(self):self.messages=None
  async def complete(self,messages,tools=None):
   self.messages=messages;return ModelResponse(text="")
 provider=Capture();planner=JsonModelPlanner(provider)
 asyncio.run(planner.next_request({"blob":"x"*100000}))
 assert len(provider.messages[1].content)<=50000
