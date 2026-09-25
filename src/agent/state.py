from typing import TypedDict, List, Dict, Optional, Any

class SREAgentState(TypedDict):
    """
    Standard state schema passed across all nodes in the LangGraph SRE state machine.
    """
    incident_id: str
    target_service: str
    trigger_alert: str
    current_metrics: Dict[str, Any]
    logs: List[str]
    anomalies_detected: List[Dict[str, Any]]
    rag_runbooks: List[Dict[str, Any]]
    diagnosis: str
    confidence: float
    proposed_actions: List[Dict[str, Any]]
    policy_approved_actions: List[Dict[str, Any]]
    actions_executed: List[Dict[str, Any]]
    verification_status: str  # RESOLVED, UNRESOLVED, ESCALATED
    verification_metrics: Dict[str, Any]
    final_report: str
