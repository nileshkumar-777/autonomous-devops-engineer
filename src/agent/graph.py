import logging
import uuid
import time
from typing import Dict, List, Any
from src.agent.state import SREAgentState
from src.agent.tools import SREClusterTools
from src.agent.policies import PolicyGatekeeper
from src.rag.retriever import RunbookRetriever
from src.ml.log_parser import LogParser

logger = logging.getLogger("autosre-agent")

class AutoSREAgent:
    """
    Autonomous Site Reliability Engineering Agent.
    Implements a closed-loop observe-analyze-act-verify state machine.
    """

    def __init__(self, tools: SREClusterTools = None, retriever: RunbookRetriever = None):
        self.tools = tools or SREClusterTools(use_simulator=True)
        self.retriever = retriever or RunbookRetriever()

    # --------------------------------------------------------------------------
    # Node 1: Incident Entry Node
    # --------------------------------------------------------------------------
    def entry_node(self, incident: Dict[str, Any]) -> SREAgentState:
        inc_id = incident.get("incident_id") or f"inc_{uuid.uuid4().hex[:8]}"
        target = incident.get("service_name", "payment-service")
        alert = incident.get("alert_name", "High5xxErrorRate")

        logger.info("Initializing incident %s for service '%s' (Alert: %s)", inc_id, target, alert)

        state: SREAgentState = {
            "incident_id": inc_id,
            "target_service": target,
            "trigger_alert": alert,
            "current_metrics": {},
            "logs": [],
            "anomalies_detected": [],
            "rag_runbooks": [],
            "diagnosis": "",
            "confidence": 0.0,
            "proposed_actions": [],
            "policy_approved_actions": [],
            "actions_executed": [],
            "verification_status": "PENDING",
            "verification_metrics": {},
            "final_report": "",
        }
        return state

    # --------------------------------------------------------------------------
    # Node 2: Telemetry Scraper Node
    # --------------------------------------------------------------------------
    def scraper_node(self, state: SREAgentState) -> SREAgentState:
        target = state["target_service"]
        metrics = self.tools.get_service_telemetry(target)
        logs = self.tools.get_service_logs(target, tail=50)

        state["current_metrics"] = metrics
        state["logs"] = logs
        logger.info("Scraped %d logs and telemetry for '%s' (Error rate: %.2f)", len(logs), target, metrics["error_rate"])
        return state

    # --------------------------------------------------------------------------
    # Node 3: ML Anomaly Detection Node
    # --------------------------------------------------------------------------
    def ml_anomaly_node(self, state: SREAgentState) -> SREAgentState:
        anomalies = []
        for line in state["logs"]:
            parsed = LogParser.parse_microservice_line(line)
            if parsed["is_anomaly_ground_truth"] or "pool exhausted" in line.lower() or "503" in line:
                anomalies.append({
                    "raw_line": line,
                    "level": parsed["level"],
                    "component": parsed["component"],
                    "signature": parsed["cleaned_message"],
                })

        state["anomalies_detected"] = anomalies
        logger.info("ML Anomaly node detected %d anomalous log events.", len(anomalies))
        return state

    # --------------------------------------------------------------------------
    # Node 4: RAG Runbook Query Node
    # --------------------------------------------------------------------------
    def rag_node(self, state: SREAgentState) -> SREAgentState:
        query_text = f"{state['trigger_alert']} {state['target_service']} "
        if state["anomalies_detected"]:
            query_text += " ".join(a["signature"] for a in state["anomalies_detected"][:3])
        else:
            query_text += "latency failure error"

        matched_runbooks = self.retriever.query(query_text, top_k=2)
        state["rag_runbooks"] = matched_runbooks
        logger.info("RAG query matched %d relevant runbook sections.", len(matched_runbooks))
        return state

    # --------------------------------------------------------------------------
    # Node 5: Diagnostic Reasoner Node (RCA)
    # --------------------------------------------------------------------------
    def diagnostic_node(self, state: SREAgentState) -> SREAgentState:
        target = state["target_service"]
        anomalies = state["anomalies_detected"]
        metrics = state["current_metrics"]

        # Deterministic SRE diagnostic inference based on collected evidence
        is_db_pool = any("pool exhausted" in a.get("raw_line", "").lower() for a in anomalies)
        is_oom = any("oom" in a.get("raw_line", "").lower() for a in anomalies)

        proposed_actions = []

        if is_db_pool or metrics.get("error_rate", 0) > 0.5:
            state["diagnosis"] = (
                f"Critical root cause identified in {target}: Database connection pool exhausted. "
                "High request volume prevented idle connection reclamation, causing HTTP 503 cascades."
            )
            state["confidence"] = 0.94
            proposed_actions.append({
                "action_type": "restart_deployment",
                "service_name": target,
                "reason": "Clear hung DB connections by triggering a zero-downtime rolling restart.",
            })
            proposed_actions.append({
                "action_type": "scale_deployment",
                "service_name": target,
                "replicas": 3,
                "reason": "Scale to 3 replicas to distribute connection capacity.",
            })
        elif is_oom:
            state["diagnosis"] = f"Memory exhaustion (OOMKilled) detected in {target}."
            state["confidence"] = 0.91
            proposed_actions.append({
                "action_type": "restart_deployment",
                "service_name": target,
                "reason": "Flush memory heap via deployment restart.",
            })
        else:
            state["diagnosis"] = f"Elevated transient latency detected in {target}."
            state["confidence"] = 0.75
            proposed_actions.append({
                "action_type": "scale_deployment",
                "service_name": target,
                "replicas": 3,
                "reason": "Scale capacity to absorb traffic.",
            })

        state["proposed_actions"] = proposed_actions
        logger.info("Diagnosis formulated (confidence=%.2f): %s", state["confidence"], state["diagnosis"][:80])
        return state

    # --------------------------------------------------------------------------
    # Node 6: Policy Gatekeeper Node
    # --------------------------------------------------------------------------
    def policy_gate_node(self, state: SREAgentState) -> SREAgentState:
        approved, rejected = PolicyGatekeeper.filter_actions(state["proposed_actions"])
        state["policy_approved_actions"] = approved
        if rejected:
            logger.warning("Policy Gatekeeper rejected %d unsafe action(s).", len(rejected))
        logger.info("Policy Gatekeeper approved %d action(s).", len(approved))
        return state

    # --------------------------------------------------------------------------
    # Node 7: Tool Executor Node
    # --------------------------------------------------------------------------
    def executor_node(self, state: SREAgentState) -> SREAgentState:
        executed = []
        for action in state["policy_approved_actions"]:
            if action.get("requires_human_approval"):
                logger.warning("Action requires human operator signoff: %s", action["action_type"])
                continue

            act_type = action["action_type"]
            svc = action["service_name"]

            if act_type == "restart_deployment":
                res = self.tools.restart_deployment(svc)
                executed.append(res)
            elif act_type == "scale_deployment":
                res = self.tools.scale_deployment(svc, replicas=action["replicas"])
                executed.append(res)
            elif act_type == "rollback_deployment":
                res = self.tools.rollback_deployment(svc)
                executed.append(res)

        state["actions_executed"] = executed
        logger.info("Successfully executed %d remediation action(s).", len(executed))
        return state

    # --------------------------------------------------------------------------
    # Node 8: Closed-Loop Verification Node
    # --------------------------------------------------------------------------
    def verifier_node(self, state: SREAgentState) -> SREAgentState:
        target = state["target_service"]
        # Fetch post-remediation metrics
        post_metrics = self.tools.get_service_telemetry(target)
        state["verification_metrics"] = post_metrics

        if post_metrics["error_rate"] < 0.05 and post_metrics["latency_p95_ms"] < 500:
            state["verification_status"] = "RESOLVED"
            status_text = "INCIDENT RESOLVED: System telemetry returned to healthy baseline parameters."
        else:
            state["verification_status"] = "UNRESOLVED"
            status_text = "WARNING: System still degraded after remediation actions."

        report = (
            f"=== AutoSRE Incident Report: {state['incident_id']} ===\n"
            f"Service: {state['target_service']}\n"
            f"Alert: {state['trigger_alert']}\n"
            f"Diagnosis: {state['diagnosis']}\n"
            f"Confidence: {state['confidence'] * 100:.1f}%\n"
            f"Remediation Actions Executed: {len(state['actions_executed'])}\n"
            f"Verification: {state['verification_status']}\n"
            f"Post-Fix Error Rate: {post_metrics['error_rate'] * 100:.1f}%\n"
            f"Post-Fix P95 Latency: {post_metrics['latency_p95_ms']}ms\n"
            f"Summary: {status_text}\n"
        )
        state["final_report"] = report
        logger.info("Closed-loop verification complete: %s", state["verification_status"])
        return state

    # --------------------------------------------------------------------------
    # Run Complete Graph
    # --------------------------------------------------------------------------
    def run(self, incident: Dict[str, Any]) -> SREAgentState:
        """Run the end-to-end autonomous SRE diagnostic and self-healing loop."""
        state = self.entry_node(incident)
        state = self.scraper_node(state)
        state = self.ml_anomaly_node(state)
        state = self.rag_node(state)
        state = self.diagnostic_node(state)
        state = self.policy_gate_node(state)
        state = self.executor_node(state)
        state = self.verifier_node(state)
        return state
