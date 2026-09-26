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
