from project_brain.scheduling import LockManager

def test_two_workers_cannot_hold_same_resource():
 l=LockManager()
 assert l.acquire("file:x","w1")
 assert not l.acquire("file:x","w2")
 assert l.release("file:x","w1")
 assert l.acquire("file:x","w2")
