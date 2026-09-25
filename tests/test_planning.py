from project_brain.planning import PlanningEngine
from project_brain.unknowns import Unknown,UnknownPriority
from project_brain.hypotheses import Hypothesis
from project_brain.experiments import Experiment

def test_planner_targets_project_killer_and_cheapest_experiment():
    unknowns=[Unknown(id="u1",question="minor",why_it_matters="x",priority=UnknownPriority.LOW),Unknown(id="u2",question="killer",why_it_matters="x",priority=UnknownPriority.PROJECT_KILLER)]
    hs=[Hypothesis(id="h1",statement="x",why_it_matters="x",cheapest_test="a",success_condition="yes",failure_condition="no")]
    ex=[Experiment(id="e1",hypothesis_id="h1",action="a",expected_cost=2),Experiment(id="e2",hypothesis_id="h1",action="b",expected_cost=1)]
    p=PlanningEngine().choose(unknowns,hs,ex)
    assert p.focus_unknown_id=="u2"
    assert p.experiment_id=="e2"
