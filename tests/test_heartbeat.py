from datetime import datetime,timezone,timedelta
from project_brain.runtime import HeartbeatMonitor

def test_worker_becomes_dead_after_timeout():
 now=datetime.now(timezone.utc);m=HeartbeatMonitor(30);m.beat("w",now)
 assert m.alive("w",now+timedelta(seconds=20))
 assert not m.alive("w",now+timedelta(seconds=31))
