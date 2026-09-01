import pytest
from app.core.security import create_access_token

def test_simulation_brute_force(client):
    token = create_access_token({"sub": "admin"})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post("/api/simulation/brute-force", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["scenario"] == "brute_force"

def test_get_playbooks(client):
    token = create_access_token({"sub": "analyst"})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/playbooks", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
