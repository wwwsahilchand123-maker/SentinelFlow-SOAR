import pytest
from app.core.security import create_access_token

def test_login_success(client):
    res = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["role"] == "ADMIN"

def test_login_invalid_password(client):
    res = client.post("/api/auth/login", json={"username": "admin", "password": "wrongpassword"})
    assert res.status_code == 401

def test_get_current_user_me(client):
    token = create_access_token({"sub": "analyst"})
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["username"] == "analyst"
    assert res.json()["role"] == "SOC_ANALYST"
