import pytest
from src.agent.policies import PolicyGatekeeper
from src.agent.tools import SREClusterTools
from src.agent.graph import AutoSREAgent

def test_policy_gatekeeper_allowlist():
    # Valid restart
    valid_act = {"action_type": "restart_deployment", "service_name": "payment-service"}
    allowed, reason, human = PolicyGatekeeper.validate_action(valid_act)
    assert allowed is True
    assert human is False

    # Valid scale
    valid_scale = {"action_type": "scale_deployment", "service_name": "order-service", "replicas": 4}
    allowed, reason, human = PolicyGatekeeper.validate_action(valid_scale)
    assert allowed is True
    assert human is False

    # Invalid action (arbitrary shell / unallowlisted)
    dangerous_act = {"action_type": "delete_all_namespaces", "service_name": "payment-service"}
    allowed, reason, human = PolicyGatekeeper.validate_action(dangerous_act)
    assert allowed is False

    # Out of bounds scale (replicas > 10)
    overscale_act = {"action_type": "scale_deployment", "service_name": "payment-service", "replicas": 50}
    allowed, reason, human = PolicyGatekeeper.validate_action(overscale_act)
    assert allowed is False

def test_policy_gatekeeper_protected_service_human_approval():
    protected_act = {"action_type": "restart_deployment", "service_name": "auth-database"}
    allowed, reason, human = PolicyGatekeeper.validate_action(protected_act)
    assert allowed is True
    assert human is True

def test_agent_end_to_end_self_healing_loop():
    agent = AutoSREAgent()
    incident = {
        "incident_id": "inc_test_4920",
        "service_name": "payment-service",
        "alert_name": "High5xxErrorRate",
    }

    result = agent.run(incident)

    assert result["incident_id"] == "inc_test_4920"
    assert result["target_service"] == "payment-service"
    assert len(result["logs"]) > 0
    assert len(result["anomalies_detected"]) > 0
    assert len(result["rag_runbooks"]) > 0
    assert "Database connection pool exhausted" in result["diagnosis"]
    assert result["confidence"] > 0.8
    assert len(result["policy_approved_actions"]) >= 2
    assert len(result["actions_executed"]) >= 2
    assert result["verification_status"] == "RESOLVED"
    assert "INCIDENT RESOLVED" in result["final_report"]
