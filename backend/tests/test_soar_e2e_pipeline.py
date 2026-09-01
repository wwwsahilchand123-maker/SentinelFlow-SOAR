import pytest
from app.core.security import create_access_token

def test_simulation_attack_injection_e2e(client):
    token = create_access_token({"sub": "analyst"})
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Trigger brute-force attack simulation
    res = client.post("/api/simulation/brute-force", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "alert_id" in data["result"]
    assert len(data["result"]["executed_playbooks"]) > 0
    
    alert_id = data["result"]["alert_id"]
    
    # 2. Check alert was persisted
    alert_res = client.get("/api/alerts", headers=headers)
    assert alert_res.status_code == 200
    alerts = alert_res.json()
    matching = [a for a in alerts if a["alert_id"] == alert_id]
    assert len(matching) == 1
    assert matching[0]["source_ip"] == "185.220.101.45"
    
    # 3. Check health endpoint reports operational components
    health_res = client.get("/api/health")
    assert health_res.status_code == 200
    assert health_res.json()["status"] == "healthy"
    
    # 4. Check global search for the newly injected IP
    search_res = client.get("/api/search?q=185.220.101.45", headers=headers)
    assert search_res.status_code == 200
    assert len(search_res.json()["results"]["alerts"]) > 0

def test_approvals_workflow(client):
    token_admin = create_access_token({"sub": "admin"})
    headers_admin = {"Authorization": f"Bearer {token_admin}"}
    
    # List approvals
    app_res = client.get("/api/approvals", headers=headers_admin)
    assert app_res.status_code == 200
    approvals = app_res.json()
    assert len(approvals) > 0
    
    pending = [a for a in approvals if a["status"] == "Pending"]
    if pending:
        target_id = pending[0]["id"]
        dec_res = client.post(
            f"/api/approvals/{target_id}/decision",
            headers=headers_admin,
            json={"decision": "Approved", "notes": "Approved by SOC Lead during test"}
        )
        assert dec_res.status_code == 200
        assert dec_res.json()["status"] == "Approved"
