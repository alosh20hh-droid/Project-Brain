from datetime import datetime,timezone,timedelta
from project_brain.runtime import LeaseManager

def test_expired_task_can_be_reclaimed():
 now=datetime.now(timezone.utc);m=LeaseManager()
 assert m.claim("t","w1",10,now)
 assert not m.claim("t","w2",10,now+timedelta(seconds=5))
 assert m.claim("t","w2",10,now+timedelta(seconds=11))
