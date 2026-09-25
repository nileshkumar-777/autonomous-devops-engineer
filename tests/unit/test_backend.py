import pytest
from fastapi.testclient import TestClient
from src.backend.app import app as backend_app

@pytest.fixture
def client():
    return TestClient(backend_app)

def test_system_status_endpoint(client):
    response = client.get("/api/system/status")
    assert response.status_code == 200
    data = response.json()
    assert "agent_status" in data
    assert "fleet_health" in data

def test_services_fleet_endpoint(client):
    response = client.get("/api/services")
    assert response.status_code == 200
    services = response.json()
    assert len(services) == 4
    names = [s["service_name"] for s in services]
    assert "payment-service" in names
    assert "user-service" in names

def test_trigger_and_self_heal_incident(client):
    payload = {
        "service_name": "payment-service",
        "alert_name": "DatabaseConnectionPoolExhausted",
        "severity": "CRITICAL",
    }
    response = client.post("/api/incidents/trigger", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "incident_id" in data
    assert data["result"]["verification_status"] == "RESOLVED"
    assert len(data["result"]["actions_executed"]) >= 1

    # Verify incident is in incident list
    list_resp = client.get("/api/incidents")
    assert list_resp.status_code == 200
    incidents = list_resp.json()
    assert any(i["id"] == data["incident_id"] for i in incidents)

    # Verify audit logs
    audit_resp = client.get("/api/audit-logs")
    assert audit_resp.status_code == 200
    logs = audit_resp.json()
    assert len(logs) >= 1
