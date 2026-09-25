from project_brain.scheduling import TaskGraph,TaskNode,LockManager,Scheduler

def test_locked_task_is_skipped():
 g=TaskGraph();g.add(TaskNode("a"));g.add(TaskNode("b"))
 locks=LockManager();locks.acquire("repo","other")
 s=Scheduler(g,locks)
 items=s.claim_ready("w",{"a":["repo"],"b":["db"]},limit=2)
 assert [x.task_id for x in items]==["b"]


def test_same_task_cannot_be_claimed_twice_without_release():
 g=TaskGraph();g.add(TaskNode("a"));s=Scheduler(g,LockManager())
 assert [x.task_id for x in s.claim_ready("w1",{},1)]==["a"]
 assert s.claim_ready("w2",{},1)==[]
