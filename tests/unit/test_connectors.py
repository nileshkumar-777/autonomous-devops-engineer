import pytest
from fastapi.testclient import TestClient
from src.backend.app import app as backend_app

@pytest.fixture
def client():
    return TestClient(backend_app)

def test_list_system_connectors(client):
    response = client.get("/api/connectors")
    assert response.status_code == 200
    connectors = response.json()
    assert len(connectors) >= 5
    types = [c["system_type"] for c in connectors]
    assert "KUBERNETES" in types
    assert "VERCEL" in types
    assert "GITHUB" in types
    assert "PROMETHEUS" in types
    assert "SLACK" in types

def test_test_system_connector_vercel(client):
    payload = {
        "system_type": "VERCEL",
        "target_endpoint": "https://api.vercel.com/v13",
        "auth_type": "BEARER_TOKEN"
    }
    response = client.post("/api/connectors/test", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert "Vercel" in data["message"]
    assert "latency_ms" in data

def test_test_system_connector_github(client):
    payload = {
        "system_type": "GITHUB",
        "target_endpoint": "https://api.github.com",
        "auth_type": "BEARER_TOKEN"
    }
    response = client.post("/api/connectors/test", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert "GitHub" in data["message"]
    assert "latency_ms" in data

def test_test_system_connector_kubernetes(client):
    payload = {
        "system_type": "KUBERNETES",
        "target_endpoint": "https://eks.us-east-1.amazonaws.com",
        "auth_type": "IAM_ROLE"
    }
    response = client.post("/api/connectors/test", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert "Kubernetes" in data["message"]

def test_add_new_system_connector(client):
    payload = {
        "name": "Google Cloud GKE Staging",
        "system_type": "KUBERNETES",
        "target_endpoint": "https://gke.us-central1.googleapis.com/v1/clusters/gke-staging",
        "auth_type": "IAM_ROLE",
        "environment": "STAGING",
        "auto_remediation_enabled": True
    }
    response = client.post("/api/connectors/add", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "successfully connected" in data["message"]
    assert data["connector"]["name"] == "Google Cloud GKE Staging"

def test_toggle_remediation(client):
    payload = {
        "connector_id": "conn_aws_eks",
        "enabled": False
    }
    response = client.post("/api/connectors/toggle", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "disabled" in data["message"]

def test_vercel_webhook_receiver(client):
    payload = {
        "type": "deployment.error",
        "payload": {
            "name": "autonomous-devops-engineer",
            "url": "autonomous-devops-engineer.vercel.app"
        }
    }
    response = client.post("/api/webhooks/vercel", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "PROCESSED"
    assert data["event"] == "deployment.error"

def test_github_webhook_receiver(client):
    payload = {
        "action": "workflow_run",
        "repository": {
            "full_name": "nileshkumar-777/autonomous-devops-engineer"
        }
    }
    response = client.post("/api/webhooks/github", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "PROCESSED"
    assert data["action"] == "workflow_run"
