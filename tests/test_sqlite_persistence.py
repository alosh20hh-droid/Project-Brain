import pytest
from project_brain.persistence import SQLiteProjectStore

def test_state_survives_new_store_instance(tmp_path):
 p=tmp_path/"brain.db"
 a=SQLiteProjectStore(p); v=a.save_state("p",{"step":3})
 b=SQLiteProjectStore(p); state,v2=b.load_state("p")
 assert state=={"step":3}; assert v==v2==1

def test_version_conflict_blocks_stale_writer(tmp_path):
 s=SQLiteProjectStore(tmp_path/"brain.db")
 s.save_state("p",{"x":1})
 with pytest.raises(RuntimeError):s.save_state("p",{"x":2},expected_version=0)
