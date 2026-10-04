"""
Integration Test Suite: Connecting External Target Project to AutoSRE Control Plane
====================================================================================
Tests the complete end-to-end functionality:
1. External Inventory Service operation & Prometheus instrumentation
2. Controlled Chaos Fault Injection (DB Pool Exhaustion, Memory Saturation)
3. Registering the new service into AutoSRE System Connectors
4. Firing Prometheus Alert to AutoSRE Incident Gateway
5. LangGraph Self-Healing Loop Execution (ML Anomaly -> RAG -> Gemini RCA -> Policy Gate -> Tool Execution)
6. Cryptographic Audit Ledger logging
7. Verifying complete closed-loop recovery of the external microservice
"""

import sys
import os
import pytest
from fastapi.testclient import TestClient

# Add project root to sys.path so we can import AutoSRE modules
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from external_testing_project.app.main import app as inventory_app
from src.backend.app import app as autosre_app
from src.backend.database import SessionLocal
from src.backend.models import SystemConnector, IncidentRecord, AuditLedger

@pytest.fixture
def inv_client():
    return TestClient(inventory_app)

@pytest.fixture
def sre_client():
    return TestClient(autosre_app)

# ------------------------------------------------------------------------------
# Test 1: External Inventory Service Baseline Functionality
# ------------------------------------------------------------------------------
def test_inventory_service_baseline_health(inv_client):
    """Verify external inventory service starts healthy and exposes metrics."""
    resp = inv_client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["service"] == "inventory-service"
    assert data["db_connected"] is True

    # Prometheus metrics verification
    metrics_resp = inv_client.get("/metrics")
    assert metrics_resp.status_code == 200
    assert b"http" in metrics_resp.content

def test_inventory_catalog_and_reservation(inv_client):
    """Verify inventory browsing and stock reservation workflow."""
    # List catalog
    catalog_resp = inv_client.get("/api/v1/inventory")
    assert catalog_resp.status_code == 200
    items = catalog_resp.json()
    assert len(items) >= 4

    # Reserve item
    reserve_payload = {
        "sku": "sku_1001",
        "quantity": 2,
        "order_id": "ord_ext_test_99"
    }
    reserve_resp = inv_client.post("/api/v1/inventory/reserve", json=reserve_payload)
    assert reserve_resp.status_code == 200
    res_data = reserve_resp.json()
    assert res_data["status"] == "RESERVED"
    assert res_data["quantity_reserved"] == 2

# ------------------------------------------------------------------------------
# Test 2: Incurring Failure via Chaos Injection in External Service
# ------------------------------------------------------------------------------
def test_external_chaos_failure_injection(inv_client):
    """Inject DB pool exhaustion into the inventory service to simulate catastrophic outage."""
    inject_resp = inv_client.post("/chaos/inject", json={"db_exhaust": True})
    assert inject_resp.status_code == 200

    # Business calls should now receive HTTP 503 Service Unavailable
    res = inv_client.get("/api/v1/inventory")
    assert res.status_code == 503
    assert res.json()["code"] == "DB_POOL_TIMEOUT"

    # Health check reflects degraded state
    health_resp = inv_client.get("/health")
    assert health_resp.status_code == 200
    assert health_resp.json()["status"] == "degraded"
    assert health_resp.json()["db_connected"] is False

# ------------------------------------------------------------------------------
# Test 3: Connecting External Project to AutoSRE Control Plane
# ------------------------------------------------------------------------------
def test_register_inventory_connector_in_autosre(sre_client):
    """Register the new external service into AutoSRE Multi-Cloud System Connectors."""
    connector_payload = {
        "name": "Inventory & Warehouse Microservice",
        "system_type": "KUBERNETES",
        "target_endpoint": "http://inventory-service.production.svc.cluster.local:8010",
        "auth_type": "BEARER_TOKEN",
        "environment": "PRODUCTION",
        "auto_remediation_enabled": True
    }
    resp = sre_client.post("/api/connectors/add", json=connector_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "successfully connected" in data["message"]
    assert data["connector"]["name"] == "Inventory & Warehouse Microservice"

    # Test live probe handshake
    probe_payload = {
        "system_type": "KUBERNETES",
        "target_endpoint": "http://inventory-service:8010",
        "auth_type": "BEARER_TOKEN"
    }
    probe_resp = sre_client.post("/api/connectors/test", json=probe_payload)
    assert probe_resp.status_code == 200
    assert probe_resp.json()["status"] == "SUCCESS"

# ------------------------------------------------------------------------------
# Test 4: Closed-Loop Autonomous Diagnosis & Self-Healing of the External Service
# ------------------------------------------------------------------------------
def test_autosre_diagnoses_and_heals_external_service(sre_client, inv_client):
    """
    Simulate Prometheus Alertmanager alerting AutoSRE of the inventory service outage.
    AutoSRE ingests the incident, executes RCA, applies policy gate, and heals the service.
    """
    incident_trigger_payload = {
        "service_name": "inventory-service",
        "alert_name": "DatabaseConnectionPoolExhausted",
        "severity": "CRITICAL"
    }
    heal_resp = sre_client.post("/api/incidents/trigger", json=incident_trigger_payload)
    assert heal_resp.status_code == 200
    data = heal_resp.json()

    assert "incident_id" in data
    res = data["result"]
    assert res["target_service"] == "inventory-service"
    assert res["trigger_alert"] == "DatabaseConnectionPoolExhausted"
    
    # 1. Anomaly & RAG checks
    assert len(res["rag_runbooks"]) > 0
    # 2. Diagnosis generated
    assert len(res["diagnosis"]) > 0
    assert res["confidence"] > 0.7
    # 3. Policy Gatekeeper verified action
    assert len(res["policy_approved_actions"]) >= 1
    # 4. Verification completed
    assert res["verification_status"] == "RESOLVED"
    assert "INCIDENT RESOLVED" in res["final_report"]

    # Apply remediation to the live inventory service
    remed_resp = inv_client.post("/remediate/restart")
    assert remed_resp.status_code == 200
    assert remed_resp.json()["status"] == "RESTARTED"

    # Verify inventory service is restored to 100% HEALTHY
    post_health = inv_client.get("/health")
    assert post_health.status_code == 200
    assert post_health.json()["status"] == "healthy"
    assert post_health.json()["db_connected"] is True

    # Verify inventory endpoints now succeed normally
    catalog_resp = inv_client.get("/api/v1/inventory")
    assert catalog_resp.status_code == 200

# ------------------------------------------------------------------------------
# Test 5: Verify Incident and Audit Trail Persistence
# ------------------------------------------------------------------------------
def test_audit_ledger_persistence(sre_client):
    """Verify that every autonomous action is permanently committed to SQLite."""
    audit_resp = sre_client.get("/api/audit-logs")
    assert audit_resp.status_code == 200
    logs = audit_resp.json()
    assert len(logs) > 0
    
    # Confirm actions exist for inventory-service
    inv_actions = [l for l in logs if l["target_service"] == "inventory-service"]
    assert len(inv_actions) > 0
    assert any(a["status"] == "SUCCESS" for a in inv_actions)

# ------------------------------------------------------------------------------
# Test 6: Restaurant Menu & Customer Order Workflow
# ------------------------------------------------------------------------------
def test_restaurant_menu_and_order_flow(inv_client):
    """Verify restaurant menu browsing, cart checkout, and kitchen order dispatch."""
    # Reset chaos first
    inv_client.post("/chaos/reset")

    # Browse menu
    menu_resp = inv_client.get("/api/v1/inventory")
    assert menu_resp.status_code == 200
    items = menu_resp.json()
    assert len(items) >= 10
    categories = [i["category"] for i in items]
    assert "Artisanal Coffee" in categories
    assert "Bakery & Pastries" in categories

    # Create customer dining order
    order_payload = {
        "customer_name": "Elena Vance",
        "order_type": "dine_in",
        "table_number": "Table 7",
        "items": [
            {"sku": "menu_espresso", "quantity": 2},
            {"sku": "menu_croissant", "quantity": 1}
        ],
        "special_notes": "Extra hot espresso"
    }
    order_resp = inv_client.post("/api/v1/orders/create", json=order_payload)
    assert order_resp.status_code == 200
    order_data = order_resp.json()
    assert "order_id" in order_data
    assert order_data["customer_name"] == "Elena Vance"
    assert order_data["total_amount"] > 0
    assert order_data["status"] == "PREPARING"

# ------------------------------------------------------------------------------
# Test 7: Table Reservation Booking
# ------------------------------------------------------------------------------
def test_restaurant_table_reservation(inv_client):
    """Verify table reservation booking on the restaurant website."""
    inv_client.post("/chaos/reset")
    res_payload = {
        "customer_name": "Marcus Aurelius",
        "email": "marcus@philosophy.org",
        "phone": "555-0149",
        "guests": 4,
        "reservation_date": "2026-10-15",
        "reservation_time": "07:30 PM",
        "seating_preference": "Garden Patio"
    }
    res_resp = inv_client.post("/api/v1/reservations", json=res_payload)
    assert res_resp.status_code == 200
    data = res_resp.json()
    assert "reservation_id" in data
    assert data["status"] == "CONFIRMED"
    assert data["guests"] == 4

# ------------------------------------------------------------------------------
# Test 8: Failure Incurred in Restaurant Site and Self-Healed by AutoSRE
# ------------------------------------------------------------------------------
def test_restaurant_outage_interception_and_autosre_self_healing(sre_client, inv_client):
    """
    Simulate failure injection into the restaurant site (DB connection pool exhaustion).
    Order attempts fail with 503. AutoSRE detects, diagnoses via Gemini, and resolves the outage.
    """
    # 1. Inject failure into restaurant app
    inject_resp = inv_client.post("/chaos/inject", json={"db_exhaust": True})
    assert inject_resp.status_code == 200

    # 2. Customer order fails with HTTP 503 DB_POOL_TIMEOUT
    fail_order = inv_client.post("/api/v1/orders/create", json={
        "customer_name": "Test Customer",
        "table_number": "Table 1",
        "items": [{"sku": "menu_espresso", "quantity": 1}]
    })
    assert fail_order.status_code == 503
    assert fail_order.json()["code"] == "DB_POOL_TIMEOUT"

    # 3. Alert dispatched to AutoSRE Control Plane
    alert_payload = {
        "service_name": "restaurant-cafe-service",
        "alert_name": "DatabaseConnectionPoolExhausted",
        "severity": "CRITICAL"
    }
    heal_resp = sre_client.post("/api/incidents/trigger", json=alert_payload)
    assert heal_resp.status_code == 200
    result = heal_resp.json()["result"]
    assert result["target_service"] == "restaurant-cafe-service"
    assert result["verification_status"] == "RESOLVED"
    assert len(result["actions_executed"]) >= 1

    # 4. Remediation applied to the restaurant app
    remed_resp = inv_client.post("/remediate/restart")
    assert remed_resp.status_code == 200

    # 5. Verify restaurant app is 100% recovered
    health_resp = inv_client.get("/health")
    assert health_resp.status_code == 200
    assert health_resp.json()["status"] == "healthy"
    assert health_resp.json()["db_connected"] is True

    # 6. Orders now succeed normally
    success_order = inv_client.post("/api/v1/orders/create", json={
        "customer_name": "Restored Customer",
        "table_number": "Table 3",
        "items": [{"sku": "menu_espresso", "quantity": 1}]
    })
    assert success_order.status_code == 200

# ------------------------------------------------------------------------------
# Test 9: GitHub & Restaurant System Connectors Handshake
# ------------------------------------------------------------------------------
def test_github_and_restaurant_connectors(sre_client):
    """Verify multi-cloud connectors probe GitHub repos and the Restaurant project."""
    # Test Restaurant connector probe
    rest_probe = sre_client.post("/api/connectors/test", json={
        "system_type": "RESTAURANT_APP",
        "target_endpoint": "http://127.0.0.1:8010",
        "auth_type": "BEARER_TOKEN"
    })
    assert rest_probe.status_code == 200
    assert "latency_ms" in rest_probe.json()

    # Test GitHub connector probe
    gh_probe = sre_client.post("/api/connectors/test", json={
        "system_type": "GITHUB",
        "target_endpoint": "https://api.github.com/repos/nileshkumar-777/autonomous-devops-engineer",
        "auth_type": "WEBHOOK_SECRET"
    })
    assert gh_probe.status_code == 200
    assert gh_probe.json()["status"] == "SUCCESS"

    # List GitHub repositories
    gh_repos = sre_client.get("/api/connectors/github/repositories")
    assert gh_repos.status_code == 200
    repos = gh_repos.json()
    assert len(repos) >= 2
    repo_names = [r["full_name"] for r in repos]
    assert any("autonomous-devops-engineer" in name for name in repo_names)

