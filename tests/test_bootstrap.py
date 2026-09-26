from project_brain.bootstrap import bootstrap

def test_bootstrap_wires_durable_safety_services(tmp_path):
 first=bootstrap(tmp_path/"brain.db")
 assert first.execution.idempotency is first.idempotency
 assert first.approvals.store is first.approval_store
 assert first.approval_store.store is first.projects
 assert first.heartbeats.store is first.projects
 assert first.leases.store is first.projects
 second=bootstrap(tmp_path/"brain.db")
 assert second.projects.path==first.projects.path
