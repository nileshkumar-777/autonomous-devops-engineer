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
            self.model = genai.GenerativeModel("gemini-1.5-flash")
            logger.info("Gemini 1.5 Flash client initialized successfully.")
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
        # If Gemini is configured, invoke it with structured prompt
        if self.model:
            try:
                report = self._call_gemini(service_name, alert_name, metrics, anomalies, runbooks)
                if report:
                    return report
            except Exception as e:
                logger.error("Gemini API call failed (%s). Falling back to deterministic SRE engine.", e)

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
- restart_deployment: Safe for clearing leaked state, hung connection pools, and memory buildup.
- scale_deployment: Safe for absorbing traffic spikes (replicas must be between 1 and 10).
- rollback_deployment: Safe for reverting a bad code release or CrashLoopBackOff.

Return ONLY a valid JSON object matching this schema:
{{
  "root_cause": "concise description of the failure cause",
  "confidence": 0.95,
  "severity": "CRITICAL",
  "recommended_actions": [
    {{
      "action_type": "restart_deployment",
      "service_name": "{service_name}",
      "reason": "Clear hung DB connections by rolling restart."
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
        """Deterministic SRE reasoning rules for instant, zero-failure diagnosis."""
        anom_str = " ".join(a.get("raw_line", "").lower() for a in anomalies)
        error_rate = metrics.get("error_rate", 0.0)

        actions = []
        if "pool exhausted" in anom_str or error_rate > 0.5:
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
        elif "oom" in anom_str or "killed" in anom_str:
            root_cause = f"Memory exhaustion (OOMKilled) in {service_name} pod container."
            severity = "HIGH"
            confidence = 0.91
            explanation = "Container heap exceeded cgroup memory limits. Immediate restart required to reclaim memory."
            actions.append(RecommendedAction(
                action_type="restart_deployment",
                service_name=service_name,
                reason="Reclaim memory buffer by restarting the affected pod."
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
