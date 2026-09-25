from project_brain.experiments import Experiment, choose_cheapest

def test_choose_cheapest_experiment():
    xs=[Experiment(id="a",hypothesis_id="h",action="expensive",expected_cost=10,expected_minutes=1),Experiment(id="b",hypothesis_id="h",action="cheap",expected_cost=1,expected_minutes=10)]
    assert choose_cheapest(xs).id == "b"
