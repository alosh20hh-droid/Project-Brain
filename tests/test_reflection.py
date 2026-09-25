from project_brain.reflection import reflect

def test_repeated_failure_changes_plan():
 r=reflect(False,False,True)
 assert r.should_change_plan
