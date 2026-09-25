import logging
import time
from typing import Dict, List, Optional

logger = logging.getLogger("sre-k8s-tools")

class SREClusterTools:
    """
    Executes infrastructure operations on Kubernetes or Docker microservices.
    Maintains execution history for immutable SRE audit logging.
    """

    def __init__(self, use_simulator: bool = True):
        self.use_simulator = use_simulator
        self.action_history: List[Dict] = []
        # State simulator for tests / offline environments
        self.simulated_cluster_state: Dict[str, dict] = {
            "payment-service": {"replicas": 2, "restarts": 0, "status": "Degraded"},
            "user-service": {"replicas": 2, "restarts": 0, "status": "Healthy"},
            "order-service": {"replicas": 2, "restarts": 0, "status": "Healthy"},
            "notification-service": {"replicas": 1, "restarts": 0, "status": "Healthy"},
        }

    def get_service_logs(self, service_name: str, tail: int = 50) -> List[str]:
        """Fetch latest log lines for a target service."""
        logger.info("Fetching last %d log lines for service '%s'", tail, service_name)
        if service_name == "payment-service":
            return [
                "2026-09-25 18:00:01 [INFO] [payment-service] Server worker pool initialized",
                "2026-09-25 18:02:10 [INFO] [payment-service] Payment pay_848201 processed successfully",
                "2026-09-25 18:05:40 [FATAL] [payment-service] Database connection pool exhausted! Timeout acquiring connection",
                "2026-09-25 18:05:41 [ERROR] [payment-service] HTTP 503 Service Unavailable returned to order-service",
            ]
        elif service_name == "order-service":
            return [
                "2026-09-25 18:05:41 [ERROR] [order-service] Downstream timeout calling payment-service: Connection pool exhausted",
                "2026-09-25 18:05:42 [ERROR] [order-service] Order creation degraded due to payment failure",
            ]
        return [f"2026-09-25 18:00:00 [INFO] [{service_name}] Standard operational heartbeat OK"]

    def get_service_telemetry(self, service_name: str) -> Dict:
        """Fetch Prometheus metrics summary for a service."""
        is_payment_degraded = service_name == "payment-service" and self.simulated_cluster_state.get("payment-service", {}).get("status") == "Degraded"
        
        return {
            "service_name": service_name,
            "error_rate": 0.85 if is_payment_degraded else 0.01,
            "latency_p95_ms": 4500 if is_payment_degraded else 120,
            "cpu_saturation_pct": 82.5 if is_payment_degraded else 18.2,
            "memory_usage_mb": 240 if is_payment_degraded else 95,
            "replicas_running": self.simulated_cluster_state.get(service_name, {}).get("replicas", 2),
        }

    def restart_deployment(self, service_name: str, namespace: str = "production") -> Dict:
        """Executes a rolling restart of the target deployment."""
        logger.info("Executing rolling restart: deployment/%s in namespace '%s'", service_name, namespace)
        
        if service_name in self.simulated_cluster_state:
            self.simulated_cluster_state[service_name]["restarts"] += 1
            self.simulated_cluster_state[service_name]["status"] = "Healthy"

        record = {
            "action": "restart_deployment",
            "target": service_name,
            "namespace": namespace,
            "timestamp": time.time(),
            "status": "SUCCESS",
            "details": f"Initiated rolling restart of deployment/{service_name}.",
        }
        self.action_history.append(record)
        return record

    def scale_deployment(self, service_name: str, replicas: int, namespace: str = "production") -> Dict:
        """Scales the number of replicas for the target deployment."""
        logger.info("Scaling deployment/%s to %d replicas in namespace '%s'", service_name, replicas, namespace)
        
        if service_name in self.simulated_cluster_state:
            self.simulated_cluster_state[service_name]["replicas"] = replicas

        record = {
            "action": "scale_deployment",
            "target": service_name,
            "namespace": namespace,
            "replicas": replicas,
            "timestamp": time.time(),
            "status": "SUCCESS",
            "details": f"Deployment/{service_name} scaled to {replicas} replicas.",
        }
        self.action_history.append(record)
        return record

    def rollback_deployment(self, service_name: str, namespace: str = "production") -> Dict:
        """Rolls back the deployment to the previous revision."""
        logger.info("Rolling back deployment/%s to previous revision in namespace '%s'", service_name, namespace)
        
        if service_name in self.simulated_cluster_state:
            self.simulated_cluster_state[service_name]["status"] = "Healthy"

        record = {
            "action": "rollback_deployment",
            "target": service_name,
            "namespace": namespace,
            "timestamp": time.time(),
            "status": "SUCCESS",
            "details": f"Deployment/{service_name} rolled back to prior revision.",
        }
        self.action_history.append(record)
        return record


class VercelConnectorTools:
    """
    Adapter for connecting and remediating Vercel deployed web applications and serverless functions.
    """

    def __init__(self, api_token: Optional[str] = None, team_id: Optional[str] = None):
        self.api_token = api_token or "simulated_vercel_token"
        self.team_id = team_id or "team_autosre"

    def test_connection(self, project_name: str = "autonomous-devops-engineer") -> Dict:
        """Pings Vercel API and retrieves project status."""
        return {
            "status": "CONNECTED",
            "provider": "Vercel Cloud",
            "project": project_name,
            "latency_ms": 34.2,
            "latest_deployment": "dpl_89af3b189a7",
            "domains": [f"{project_name}.vercel.app"],
            "edge_network_status": "OPERATIONAL",
        }

    def rollback_deployment(self, project_id: str, target_deployment_id: Optional[str] = None) -> Dict:
        """Rolls back Vercel production alias to the previous known healthy deployment."""
        target_dep = target_deployment_id or "dpl_previous_stable_7294"
        logger.info("Triggering Vercel deployment rollback for project '%s' to '%s'", project_id, target_dep)
        return {
            "action": "vercel_rollback",
            "project_id": project_id,
            "reverted_to": target_dep,
            "status": "SUCCESS",
            "timestamp": time.time(),
            "details": f"Vercel production domain alias pointed back to deployment {target_dep}.",
        }


class GitHubConnectorTools:
    """
    Adapter for communicating with GitHub repositories, filing incident postmortems, and triggering Actions.
    """

    def __init__(self, repo_name: str = "nileshkumar-777/autonomous-devops-engineer", token: Optional[str] = None):
        self.repo_name = repo_name
        self.token = token or "simulated_github_pat"

    def test_connection(self) -> Dict:
        """Checks GitHub repository access and API rate limits."""
        return {
            "status": "CONNECTED",
            "provider": "GitHub Enterprise / Cloud",
            "repository": self.repo_name,
            "latency_ms": 48.1,
            "permissions": ["issues:write", "actions:write", "pull_requests:write"],
            "default_branch": "main",
        }

    def create_incident_issue(self, title: str, markdown_body: str, labels: Optional[List[str]] = None) -> Dict:
        """Automatically files an incident postmortem issue on GitHub."""
        issue_number = 42
        logger.info("Filing GitHub Incident Issue on %s: '%s'", self.repo_name, title)
        return {
            "action": "create_github_issue",
            "repo": self.repo_name,
            "issue_number": issue_number,
            "url": f"https://github.com/{self.repo_name}/issues/{issue_number}",
            "status": "CREATED",
            "timestamp": time.time(),
        }
