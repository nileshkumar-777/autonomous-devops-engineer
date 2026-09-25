import pytest
from fastapi.testclient import TestClient
from src.ml.log_parser import LogParser
from src.ml.inference_api import app as ml_app

@pytest.fixture
def ml_client():
    return TestClient(ml_app)

def test_log_parser_token_masking():
    raw_msg = "Connection from 192.168.1.105 failed at 0xdeadbeef with transaction e7b1029c-a1e4-4d8f-9a11-123456789abc for 450 requests"
    masked = LogParser.mask_tokens(raw_msg)
    assert "<IP>" in masked
    assert "<HEX>" in masked
    assert "<UUID>" in masked
    assert "<NUM>" in masked
    assert "192.168.1.105" not in masked
    assert "0xdeadbeef" not in masked

def test_log_parser_microservice_format():
    line = "2026-09-25 18:05:40 [ERROR] [payment-service] Database connection pool exhausted"
    parsed = LogParser.parse_microservice_line(line)
    assert parsed["level"] == "ERROR"
    assert parsed["component"] == "payment-service"
    assert parsed["is_anomaly_ground_truth"] is True

def test_ml_health_endpoint(ml_client):
    response = ml_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert data["model_type"] == "IsolationForest"

def test_ml_predict_normal_log(ml_client):
    log = "2026-09-25 18:05:40 [INFO] [order-service] Order ord_999 created successfully"
    resp = ml_client.post("/api/v1/predict", json={"log_line": log, "service_name": "order-service"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["level"] == "INFO"
    assert data["severity"] == "NORMAL"
    assert data["is_anomaly"] is False

def test_ml_predict_anomaly_log(ml_client):
    log = "2026-09-25 18:05:40 [FATAL] [payment-service] FATAL: Database connection pool exhausted! Unable to acquire connection from pool"
    resp = ml_client.post("/api/v1/predict", json={"log_line": log, "service_name": "payment-service"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_anomaly"] is True
    assert data["severity"] in ["CRITICAL", "HIGH"]

def test_ml_predict_batch_logs(ml_client):
    logs = [
        "2026-09-25 18:00:00 [INFO] [user-service] Health check ping OK",
        "2026-09-25 18:00:01 [INFO] [user-service] Profile fetched for user usr_101",
        "2026-09-25 18:00:02 [ERROR] [user-service] Out of memory allocation failure in worker thread",
        "2026-09-25 18:00:03 [FATAL] [user-service] Process killed by kernel: OOMKilled",
    ]
    resp = ml_client.post("/api/v1/predict/batch", json={"log_lines": logs, "service_name": "user-service"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_logs"] == 4
    assert data["anomaly_count"] == 2
    assert data["anomaly_rate"] == 0.5
    assert data["system_status"] == "ANOMALOUS"
    assert len(data["anomalous_events"]) == 2
