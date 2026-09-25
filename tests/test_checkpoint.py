from project_brain.checkpoint import JsonCheckpointStore

def test_checkpoint_roundtrip(tmp_path):
    store=JsonCheckpointStore(tmp_path/"state.json")
    store.save({"goal":"x","count":2})
    assert store.load()=={"goal":"x","count":2}
