from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint_returns_contract():
    response = client.get("/api/health")

    assert response.status_code == 200
    payload = response.json()

    assert payload["status"] in {"healthy", "degraded"}
    assert payload["app_name"]
    assert payload["version"]
    assert "timestamp" in payload
    assert "latency_ms" in payload

    components = payload["components"]
    assert set(components) >= {
        "database",
        "threat_intelligence",
        "playbook_engine",
        "response_engine",
    }
    assert components["database"]["status"] in {"healthy", "unhealthy"}
