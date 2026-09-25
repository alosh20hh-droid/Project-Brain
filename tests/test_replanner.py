from project_brain.replanner import assess_replan

def test_replan_on_unverified_result():
    assert assess_replan(False,False,False).should_replan

def test_continue_on_verified_result():
    assert not assess_replan(True,False,False).should_replan
