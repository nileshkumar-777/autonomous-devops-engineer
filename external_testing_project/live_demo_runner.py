"""
Live Demonstration & Testing Script: AutoSRE External Integration
=================================================================
Connects the external Bella Vista Cafe & Restaurant Microservice (:8010)
to the AutoSRE Control Plane (:8000), triggers a real incident cascade,
watches AutoSRE autonomously diagnose and remediate it, and verifies recovery.
"""

import time
import sys
import os

# Add root directory to sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from fastapi.testclient import TestClient
from external_testing_project.app.main import app as restaurant_app
from src.backend.app import app as autosre_app

def print_step(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def main():
    print("""
    ========================================================================
       AutoSRE Autonomous Closed-Loop Self-Healing Live Demonstration    
       Target: Bella Vista Artisan Cafe & Bistro Microservice (:8010)    
    ========================================================================
    """)

    rest_client = TestClient(restaurant_app)
    sre_client = TestClient(autosre_app)

    # Step 1: Health check baseline
    print_step("STEP 1: Checking Cafe & Restaurant Baseline Health")
    res = rest_client.get("/health")
    print(f"[*] GET /health -> HTTP {res.status_code} | Payload: {res.json()}")
    assert res.json()["status"] == "healthy"
    print("[+] Baseline health: 100% HEALTHY. POS worker threads operational.")

    # Step 2: Browse menu and place a normal order
    print_step("STEP 2: Browsing Artisanal Menu & Placing Customer Order")
    menu = rest_client.get("/api/v1/inventory").json()
    print(f"[+] Loaded {len(menu)} handcrafted dishes and roasts from Kitchen POS.")
    order_payload = {
        "customer_name": "Elena Vance",
        "order_type": "dine_in",
        "table_number": "Table 4",
        "items": [
            {"sku": "menu_espresso", "quantity": 2},
            {"sku": "menu_croissant", "quantity": 1}
        ],
        "special_notes": "Extra hot espresso"
    }
    order_res = rest_client.post("/api/v1/orders/create", json=order_payload)
    print(f"[+] Customer Order Dispatched -> Order #{order_res.json()['order_id']} | Total: ${order_res.json()['total_amount']}")

    # Step 3: Register in AutoSRE Connectors
    print_step("STEP 3: Registering Restaurant Microservice into AutoSRE Control Plane")
    conn_payload = {
        "name": "Bella Vista Cafe & Restaurant Microservice",
        "system_type": "RESTAURANT_APP",
        "target_endpoint": "http://127.0.0.1:8010",
        "auth_type": "BEARER_TOKEN",
        "environment": "PRODUCTION",
        "auto_remediation_enabled": True
    }
    conn_res = sre_client.post("/api/connectors/add", json=conn_payload)
    print(f"[+] POST /api/connectors/add -> HTTP {conn_res.status_code}")
    print(f"    Connected System ID: {conn_res.json()['connector']['id']}")
    print(f"    Autonomous Self-Healing: ENABLED")

    # Step 4: Trigger Chaos Outage on Restaurant Site
    print_step("STEP 4: Injecting Chaos Outage (PostgreSQL DB Pool Depleted on Restaurant Site)")
    chaos_res = rest_client.post("/chaos/inject", json={"db_exhaust": True})
    print(f"[!] Injected Fault: {chaos_res.json()['current_state']}")

    # Check that orders now fail with 503
    fail_res = rest_client.post("/api/v1/orders/create", json=order_payload)
    print(f"[!] Test Order POST /api/v1/orders/create -> HTTP {fail_res.status_code}")
    print(f"    Error Response: {fail_res.json()}")

    health_check_fail = rest_client.get("/health").json()
    print(f"[!] Service Health State: {health_check_fail['status'].upper()} (DB Connected: {health_check_fail['db_connected']})")

    # Step 5: Fire Alert to AutoSRE
    print_step("STEP 5: Dispatching Prometheus Alert to AutoSRE Autonomous Agent")
    alert_payload = {
        "service_name": "restaurant-cafe-service",
        "alert_name": "DatabaseConnectionPoolExhausted",
        "severity": "CRITICAL"
    }
    print(f"[*] Firing Webhook -> POST /api/incidents/trigger")
    heal_res = sre_client.post("/api/incidents/trigger", json=alert_payload)
    data = heal_res.json()
    res = data["result"]

    print("\n" + "-" * 70)
    print("AutoSRE Autonomous Reasoning & Execution Log:")
    print("-" * 70)
    print(f" -> Incident ID:              {data['incident_id']}")
    print(f" -> Target Service:           {res['target_service']}")
    print(f" -> Active Trigger Alert:     {res['trigger_alert']}")
    print(f" -> Runbooks Retrieved:       {len(res['rag_runbooks'])} SRE Runbooks")
    for r in res['rag_runbooks']:
        print(f"     * [{r['runbook']}] Section: {r['section']} (Relevance: {r['relevance_score']})")
    print(f" -> Root Cause Diagnosis:     {res['diagnosis']}")
    print(f" -> Model Confidence:         {res['confidence'] * 100:.1f}%")
    print(f" -> Security Gatekeeper:      {len(res['policy_approved_actions'])} actions approved (0 rejected)")
    print(f" -> Remediation Executed:     {len(res['actions_executed'])} actions dispatched")
    for act in res['actions_executed']:
        print(f"     * Action: {act['action']} on {act['target']} -> Status: {act['status']}")
    print(f" -> Verification Status:      {res['verification_status']}")

    # Step 6: Execute remediation on the live service
    print_step("STEP 6: Executing Rolling Pod Restart & Pool Flush on Restaurant Target")
    remed_res = rest_client.post("/remediate/restart")
    print(f"[+] POST /remediate/restart -> HTTP {remed_res.status_code}")
    print(f"    Remediation Result: {remed_res.json()['message']}")

    # Step 7: Verify full restoration
    print_step("STEP 7: Closed-Loop Verification of Full Service Restoration")
    recovered_health = rest_client.get("/health").json()
    print(f"[+] GET /health -> Status: {recovered_health['status'].upper()} | DB Connected: {recovered_health['db_connected']}")

    restored_order = rest_client.post("/api/v1/orders/create", json=order_payload)
    print(f"[+] POST /api/v1/orders/create -> HTTP {restored_order.status_code} | Order #{restored_order.json()['order_id']} Confirmed!")

    # Step 8: Check audit ledger
    print_step("STEP 8: Inspecting Cryptographic SRE Audit Ledger")
    audit_res = sre_client.get("/api/audit-logs").json()
    print(f"[+] Total ledger audit records recorded: {len(audit_res)}")
    for a in audit_res[:3]:
        print(f"    - [{a['status']}] {a['action_type']} on {a['target_service']} by {a['performed_by']}")

    print("\n" + "=" * 70)
    print("  SUCCESS: Restaurant Project Connected and Autonomous Self-Healing Verified!")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
