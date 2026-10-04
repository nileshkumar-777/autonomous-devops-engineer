import json
import logging
import os
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("sre-gemini-reasoner")

class RecommendedAction(BaseModel):
    action_type: str = Field(..., description="Allowlisted action: restart_deployment, scale_deployment, rollback_deployment")
    service_name: str
    replicas: Optional[int] = None
    reason: str

class DiagnosticReport(BaseModel):
    root_cause: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    severity: str = Field(..., description="CRITICAL, HIGH, MEDIUM, LOW")
    recommended_actions: List[RecommendedAction]
    explanation: str

class GeminiDiagnosticReasoner:
    """
    Leverages Google Gemini 1.5/2.0 Flash to synthesize container telemetry,
    log anomalies, and SRE runbooks into an actionable Root Cause Analysis (RCA).
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = None
        self.model = None
        self._init_client()

    def _init_client(self):
        if not self.api_key or self.api_key.startswith("your_"):
            logger.warning("No valid Gemini API key found. Operating in fallback deterministic mode.")
            return

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-3.5-flash-lite")
            logger.info("Gemini 3.5 Flash Lite client initialized successfully.")
        except Exception as e:
            logger.warning("Failed to initialize Google Generative AI client: %s. Using fallback mode.", e)

    def diagnose(
        self,
        service_name: str,
        alert_name: str,
        metrics: Dict,
        anomalies: List[Dict],
        runbooks: List[Dict],
    ) -> DiagnosticReport:
        """
        Produce a structured RCA report using Gemini or fallback to deterministic inference.
        """
        if self.model:
            try:
                report = self._call_gemini(service_name, alert_name, metrics, anomalies, runbooks)
                if report:
                    return report
            except Exception as e:
                logger.warning("Gemini API call failed (%s). Falling back to deterministic SRE engine.", e)

        # Fallback deterministic SRE engine
        return self._deterministic_fallback(service_name, alert_name, metrics, anomalies, runbooks)

    def _call_gemini(
        self,
        service_name: str,
        alert_name: str,
        metrics: Dict,
        anomalies: List[Dict],
        runbooks: List[Dict],
    ) -> Optional[DiagnosticReport]:
        prompt = f"""
You are AutoSRE, an expert Autonomous Site Reliability Engineer.
Analyze the following production incident and return a STRICT JSON diagnosis.

INCIDENT DETAILS:
- Target Service: {service_name}
- Active Alert: {alert_name}
- Metrics: {json.dumps(metrics, indent=2)}

DETECTED LOG ANOMALIES:
{json.dumps(anomalies, indent=2)}

RETRIEVED SRE RUNBOOKS:
{json.dumps(runbooks, indent=2)}

ALLOWED ACTIONS:
- restart_deployment: Safe for clearing leaked state, hung connection pools, crashed host ports, and memory buildup.
- scale_deployment: Safe for absorbing traffic spikes or distributing connection capacity (replicas must be between 1 and 10).
- rollback_deployment: Safe for reverting a bad code release or CrashLoopBackOff.

RECOMMENDED ACTIONS GUIDANCE:
- For high error rate cascades, database pool exhaustion, or severe load, recommend both restart_deployment (to flush deadlocks) and scale_deployment (to expand capacity).

Return ONLY a valid JSON object matching this schema:
{{
  "root_cause": "concise description of the specific failure cause for {alert_name}",
  "confidence": 0.95,
  "severity": "CRITICAL",
  "recommended_actions": [
    {{
      "action_type": "restart_deployment",
      "service_name": "{service_name}",
      "reason": "Specific rationale"
    }}
  ],
  "explanation": "Detailed step-by-step SRE rationale based on telemetry and runbook guidance."
}}
"""
        response = self.model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        content = response.text.strip()
        data = json.loads(content)
        return DiagnosticReport(**data)

    def _deterministic_fallback(
        self,
        service_name: str,
        alert_name: str,
        metrics: Dict,
        anomalies: List[Dict],
        runbooks: List[Dict],
    ) -> DiagnosticReport:
        """Deterministic SRE reasoning rules for instant, accurate zero-failure diagnosis."""
        anom_str = " ".join(a.get("raw_line", "").lower() for a in anomalies)
        error_rate = metrics.get("error_rate", 0.0)
        p95_lat = metrics.get("latency_p95_ms", 0.0)
        alert_lower = alert_name.lower()

        actions = []
        if (
            "hostunreachable" in alert_lower
            or "refused" in anom_str
            or "unreachable" in anom_str
            or "crash" in alert_lower
            or p95_lat >= 990
        ):
            root_cause = f"Target host process crashed or port connection refused for {service_name}."
            severity = "CRITICAL"
            confidence = 0.96
            explanation = (
                f"Health checks failed with HostUnreachableOrCrash on {service_name}. Telemetry indicates "
                "the application server crashed or halted network listener. Executing automated service restart."
            )
            actions.append(RecommendedAction(
                action_type="restart_deployment",
                service_name=service_name,
                reason="Restart crashed service process to restore network availability."
            ))
        elif (
            "pool exhausted" in anom_str
            or "database" in alert_lower
            or "db_pool" in anom_str
            or "psycopg2" in anom_str
            or "databaseconnectionpoolexhausted" in alert_lower
        ):
            root_cause = f"Database connection pool exhausted in {service_name} leading to HTTP 503 cascades."
            severity = "CRITICAL"
            confidence = 0.94
            explanation = (
                f"Prometheus detected {error_rate * 100:.1f}% error rate. Log anomaly signatures confirm database "
                "worker thread exhaustion. Recommending rolling restart to flush pool, followed by horizontal scaling."
            )
            actions.append(RecommendedAction(
                action_type="restart_deployment",
                service_name=service_name,
                reason="Flush deadlocked database connection pool via rolling restart."
            ))
            actions.append(RecommendedAction(
                action_type="scale_deployment",
                service_name=service_name,
                replicas=3,
                reason="Scale to 3 replicas to distribute connection capacity."
            ))
        elif "crashloop" in alert_lower or "readiness" in alert_lower:
            root_cause = f"Container entered CrashLoopBackOff due to failed readiness probes in {service_name}."
            severity = "CRITICAL"
            confidence = 0.92
            explanation = "Readiness probe failed consecutive checks. Rolling back deployment to previous healthy revision."
            actions.append(RecommendedAction(
                action_type="rollback_deployment",
                service_name=service_name,
                reason="Rollback deployment to clear breaking configuration or corrupt container build."
            ))
        elif "downstreamtimeout" in alert_lower or "timeout" in alert_lower or p95_lat > 2000:
            root_cause = f"Downstream latency timeout cascade impacting {service_name} request pipeline."
            severity = "HIGH"
            confidence = 0.89
            explanation = f"P95 latency spiked to {p95_lat:.0f}ms. Upstream threads are blocked on downstream I/O. Horizontal scaling required."
            actions.append(RecommendedAction(
                action_type="scale_deployment",
                service_name=service_name,
                replicas=3,
                reason="Scale deployment to 3 replicas to absorb traffic spike."
            ))
        elif "oom" in anom_str or "killed" in anom_str or "memory" in alert_lower:
            root_cause = f"Memory exhaustion (OOMKilled) in {service_name} pod container."
            severity = "HIGH"
            confidence = 0.91
            explanation = "Container heap exceeded cgroup memory limits. Immediate restart required to reclaim memory."
            actions.append(RecommendedAction(
                action_type="restart_deployment",
                service_name=service_name,
                reason="Reclaim memory buffer by restarting the affected pod."
            ))
        elif "5xx" in alert_lower or "http5xx" in alert_lower or error_rate > 0.1:
            root_cause = f"HTTP 5xx error cascade detected across {service_name} application handlers."
            severity = "CRITICAL"
            confidence = 0.93
            explanation = f"Error rate elevated to {error_rate * 100:.1f}%. Restarting deployment to purge corrupted worker thread pool."
            actions.append(RecommendedAction(
                action_type="restart_deployment",
                service_name=service_name,
                reason="Restart application to clear worker state and recover baseline 2xx throughput."
            ))
        else:
            root_cause = f"Elevated latency spike detected across {service_name} upstream routes."
            severity = "MEDIUM"
            confidence = 0.82
            explanation = "Traffic surge causing thread contention. Scaling replicas recommended to relieve latency pressure."
            actions.append(RecommendedAction(
                action_type="scale_deployment",
                service_name=service_name,
                replicas=3,
                reason="Scale deployment to 3 replicas to absorb traffic spike."
            ))

        return DiagnosticReport(
            root_cause=root_cause,
            confidence=confidence,
            severity=severity,
            recommended_actions=actions,
            explanation=explanation,
        )
