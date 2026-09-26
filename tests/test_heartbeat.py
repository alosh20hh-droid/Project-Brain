from datetime import datetime,timezone,timedelta
from project_brain.runtime import HeartbeatMonitor

def test_worker_becomes_dead_after_timeout():
 now=datetime.now(timezone.utc);m=HeartbeatMonitor(30);m.beat("w",now)
 assert m.alive("w",now+timedelta(seconds=20))
 assert not m.alive("w",now+timedelta(seconds=31))


def test_monitor_reads_fresh_heartbeat_written_by_another_process(tmp_path):
 from project_brain.persistence import SQLiteProjectStore
 db=tmp_path/"brain.db";base=datetime.now(timezone.utc)
 a=HeartbeatMonitor(90,SQLiteProjectStore(db));b=HeartbeatMonitor(90,SQLiteProjectStore(db))
 a.beat("w",base);assert a.alive("w",base+timedelta(seconds=10))
 b.beat("w",base+timedelta(seconds=80))
 assert a.alive("w",base+timedelta(seconds=100))
