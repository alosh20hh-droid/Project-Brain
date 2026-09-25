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
