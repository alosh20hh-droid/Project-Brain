from project_brain.deduplication import work_fingerprint,WorkHistory

def test_same_work_is_detected():
 h=WorkHistory(); f=work_fingerprint("Goal","Research",["No spend"])
 h.mark(f)
 assert h.seen(work_fingerprint(" goal "," research ",[" no spend "]))
