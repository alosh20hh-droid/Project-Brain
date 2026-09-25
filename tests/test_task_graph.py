import pytest
from project_brain.scheduling import TaskGraph,TaskNode

def test_dependency_controls_readiness():
 g=TaskGraph();g.add(TaskNode("a"));g.add(TaskNode("b",{"a"}))
 assert [x.id for x in g.ready()]==["a"]
 g.nodes["a"].completed=True
 assert [x.id for x in g.ready()]==["b"]

def test_cycle_is_rejected():
 g=TaskGraph();g.add(TaskNode("a",{"b"}));g.add(TaskNode("b",{"a"}))
 with pytest.raises(ValueError):g.validate()
