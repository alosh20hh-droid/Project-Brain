from project_brain.model.registry import ModelRegistry
from project_brain.model.mock import MockModelProvider

def test_registry_keeps_model_provider_swappable():
    r=ModelRegistry(); p=MockModelProvider([])
    r.register("test",p)
    assert r.get("test") is p
