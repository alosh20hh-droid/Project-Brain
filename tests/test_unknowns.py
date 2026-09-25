from project_brain.unknowns import Unknown, UnknownPriority, choose_next_unknown

def test_project_killer_first():
    xs=[Unknown(id="a",question="minor",why_it_matters="x",priority=UnknownPriority.LOW),Unknown(id="b",question="fatal?",why_it_matters="x",priority=UnknownPriority.PROJECT_KILLER)]
    assert choose_next_unknown(xs).id=="b"
