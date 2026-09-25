from project_brain.recovery import decide_retry

def test_repeated_failure_forces_replan():
    d=decide_retry(attempts=2,max_attempts=5,same_error_count=2)
    assert d.retry is False
