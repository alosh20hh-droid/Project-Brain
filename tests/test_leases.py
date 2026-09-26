from datetime import datetime,timezone,timedelta
from project_brain.runtime import LeaseManager

def test_expired_task_can_be_reclaimed():
 now=datetime.now(timezone.utc);m=LeaseManager()
 assert m.claim("t","w1",10,now)
 assert not m.claim("t","w2",10,now+timedelta(seconds=5))
 assert m.claim("t","w2",10,now+timedelta(seconds=11))


def test_expired_owner_cannot_resurrect_lease():
 now=datetime.now(timezone.utc)
 m=LeaseManager();assert m.claim("t","old",seconds=1,now=now)
 assert not m.renew("t","old",seconds=10,now=now+timedelta(seconds=2))
 assert m.claim("t","new",seconds=10,now=now+timedelta(seconds=2))
 assert not m.renew("t","old",seconds=10,now=now+timedelta(seconds=3))


def test_two_runtime_instances_cannot_hold_same_live_lease(tmp_path):
 from project_brain.persistence import SQLiteProjectStore
 db=tmp_path/"brain.db";now=datetime.now(timezone.utc)
 first=LeaseManager(SQLiteProjectStore(db));second=LeaseManager(SQLiteProjectStore(db))
 assert first.claim("same-task","worker-1",30,now)
 assert not second.claim("same-task","worker-2",30,now)
 assert second.claim("same-task","worker-2",30,now+timedelta(seconds=31))
 assert not first.renew("same-task","worker-1",30,now+timedelta(seconds=32))
