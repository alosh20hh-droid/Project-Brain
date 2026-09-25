from project_brain.scheduling import TaskGraph,TaskNode,LockManager,Scheduler

def test_locked_task_is_skipped():
 g=TaskGraph();g.add(TaskNode("a"));g.add(TaskNode("b"))
 locks=LockManager();locks.acquire("repo","other")
 s=Scheduler(g,locks)
 items=s.claim_ready("w",{"a":["repo"],"b":["db"]},limit=2)
 assert [x.task_id for x in items]==["b"]
