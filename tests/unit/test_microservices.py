import importlib.util
import os
import sys
import pytest
from fastapi.testclient import TestClient

def load_app_from_path(service_folder: str):
    file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), f"../../src/microservices/{service_folder}/app/main.py")
    )
    module_name = service_folder.replace("-", "_") + "_main"
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module.app

user_app = load_app_from_path("user-service")
payment_app = load_app_from_path("payment-service")
order_app = load_app_from_path("order-service")
notify_app = load_app_from_path("notification-service")

@pytest.fixture
def user_client():
    return TestClient(user_app)

@pytest.fixture
def payment_client():
    return TestClient(payment_app)

@pytest.fixture
def order_client():
    return TestClient(order_app)

@pytest.fixture
def notify_client():
    return TestClient(notify_app)

# ------------------------------------------------------------------------------
# 1. User Service Tests
# ------------------------------------------------------------------------------
def test_user_service_health(user_client):
    response = user_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "user-service"

def test_user_service_metrics(user_client):
    response = user_client.get("/metrics")
    assert response.status_code == 200
    assert b"process_cpu" in response.content or b"http" in response.content

def test_user_service_crud(user_client):
    # List users
    resp = user_client.get("/api/v1/users")
    assert resp.status_code == 200
    assert len(resp.json()) >= 3

    # Create user
    new_user = {"name": "Test User", "email": "test@example.com", "tier": "gold"}
    create_resp = user_client.post("/api/v1/users", json=new_user)
    assert create_resp.status_code == 201
    created_id = create_resp.json()["id"]

    # Fetch user
    get_resp = user_client.get(f"/api/v1/users/{created_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Test User"

def test_user_service_chaos(user_client):
    inject_resp = user_client.post("/chaos/inject", json={"error_rate": 1.0})
    assert inject_resp.status_code == 200
    
    reset_resp = user_client.post("/chaos/reset")
    assert reset_resp.status_code == 200
    assert reset_resp.json()["status"] == "chaos_cleared"

# ------------------------------------------------------------------------------
# 2. Payment Service Tests
# ------------------------------------------------------------------------------
def test_payment_service_health(payment_client):
    response = payment_client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "payment-service"

def test_payment_processing(payment_client):
    pay_data = {
        "order_id": "ord_test_001",
        "user_id": "usr_101",
        "amount": 99.50,
        "currency": "USD"
    }
    response = payment_client.post("/api/v1/payments", json=pay_data)
    assert response.status_code == 201
    result = response.json()
    assert result["status"] == "SUCCESS"
    assert result["order_id"] == "ord_test_001"

def test_payment_db_pool_exhaustion_chaos(payment_client):
    # Trigger DB exhaustion
    payment_client.post("/chaos/inject", json={"db_exhaust": True})
    
    # Call should receive 503
    pay_data = {"order_id": "ord_fail", "user_id": "usr_101", "amount": 10.0}
    response = payment_client.post("/api/v1/payments", json=pay_data)
    assert response.status_code == 503
    assert response.json()["code"] == "DB_POOL_TIMEOUT"

    # Reset
    payment_client.post("/chaos/reset")
    resp_normal = payment_client.post("/api/v1/payments", json=pay_data)
    assert resp_normal.status_code == 201

# ------------------------------------------------------------------------------
# 3. Notification Service Tests
# ------------------------------------------------------------------------------
def test_notification_service_health(notify_client):
    response = notify_client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "notification-service"

def test_notification_dispatch(notify_client):
    notif_data = {
        "recipient": "sre-team@company.internal",
        "channel": "slack",
        "subject": "CRITICAL: Database Latency Spike",
        "body": "Payment service pool timeout detected by AutoSRE."
    }
    response = notify_client.post("/api/v1/notify", json=notif_data)
    assert response.status_code == 202
    assert "notification_id" in response.json()

# ------------------------------------------------------------------------------
# 4. Order Service Tests
# ------------------------------------------------------------------------------
def test_order_service_health(order_client):
    response = order_client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "order-service"

def test_order_service_chaos(order_client):
    inject_resp = order_client.post("/chaos/inject", json={"error_rate": 1.0})
    assert inject_resp.status_code == 200
    assert inject_resp.json()["status"] == "chaos_injected"

    reset_resp = order_client.post("/chaos/reset")
    assert reset_resp.status_code == 200
    assert reset_resp.json()["status"] == "chaos_cleared"

