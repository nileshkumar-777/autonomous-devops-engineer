import os
import time
import uuid
from typing import Dict, List, Optional
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.backend.database import engine, Base, get_db
from src.backend.models import IncidentRecord, AuditLedger
from src.agent.graph import AutoSREAgent
from src.agent.tools import SREClusterTools

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AutoSRE Control Plane API",
    description="Backend orchestration engine and database for Autonomous DevOps Incident Management.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cluster_tools = SREClusterTools(use_simulator=True)
agent = AutoSREAgent(tools=cluster_tools)

class TriggerIncidentRequest(BaseModel):
    service_name: str = "payment-service"
    alert_name: str = "High5xxErrorRate"
    severity: Optional[str] = "CRITICAL"

class ActionApprovalRequest(BaseModel):
    audit_id: int
    approved: bool

# ------------------------------------------------------------------------------
# API Endpoints
# ------------------------------------------------------------------------------

@app.get("/api/system/status")
def get_system_status(db: Session = Depends(get_db)):
    total_incidents = db.query(IncidentRecord).count()
    active_incidents = db.query(IncidentRecord).filter(IncidentRecord.status.in_(["INVESTIGATING", "ACTIVE", "PENDING_APPROVAL"])).count()
    resolved_incidents = db.query(IncidentRecord).filter(IncidentRecord.status == "RESOLVED").count()
    total_actions = db.query(AuditLedger).count()

    return {
        "agent_status": "ARMED_AUTONOMOUS",
        "llm_engine": "Gemini 1.5 Flash (Hybrid Fallback)",
        "total_incidents": total_incidents,
        "active_incidents": active_incidents,
        "resolved_incidents": resolved_incidents,
        "total_remediations_executed": total_actions,
        "cluster_health": "DEGRADED" if active_incidents > 0 else "HEALTHY",
        "fleet_health": "DEGRADED" if active_incidents > 0 else "HEALTHY",
    }

@app.get("/api/services")
def get_services_fleet():
    services = ["user-service", "payment-service", "order-service", "notification-service"]
    fleet = []
    for svc in services:
        telemetry = cluster_tools.get_service_telemetry(svc)
        status_flag = "HEALTHY"
        if telemetry["error_rate"] > 0.1:
            status_flag = "CRITICAL"
        elif telemetry["latency_p95_ms"] > 1000:
            status_flag = "DEGRADED"

        fleet.append({
            "service_name": svc,
            "status": status_flag,
            "error_rate": telemetry["error_rate"],
            "p95_latency_ms": telemetry["latency_p95_ms"],
            "cpu_saturation_pct": telemetry["cpu_saturation_pct"],
            "memory_usage_mb": telemetry["memory_usage_mb"],
            "replicas": telemetry["replicas_running"],
        })
    return fleet

@app.get("/api/incidents")
def list_incidents(limit: int = 20, db: Session = Depends(get_db)):
    incidents = db.query(IncidentRecord).order_by(IncidentRecord.created_at.desc()).limit(limit).all()
    return incidents

@app.get("/api/incidents/{incident_id}")
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    inc = db.query(IncidentRecord).filter(IncidentRecord.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    actions = db.query(AuditLedger).filter(AuditLedger.incident_id == incident_id).all()
    return {
        "incident": inc,
        "audit_actions": actions,
    }

@app.post("/api/incidents/trigger")
def trigger_and_heal_incident(req: TriggerIncidentRequest, db: Session = Depends(get_db)):
    """
    Triggers an incident, executes the full LangGraph AutoSRE self-healing loop,
    and commits the incident report and audit records to SQLite.
    """
    inc_id = f"inc_{uuid.uuid4().hex[:8]}"

    # Execute Agent Loop
    incident_input = {
        "incident_id": inc_id,
        "service_name": req.service_name,
        "alert_name": req.alert_name,
    }
    result = agent.run(incident_input)

    # Persist Incident
    incident_record = IncidentRecord(
        id=inc_id,
        service_name=result["target_service"],
        alert_name=result["trigger_alert"],
        severity=req.severity or "CRITICAL",
        status=result["verification_status"],
        diagnosis=result["diagnosis"],
        confidence=result["confidence"],
        created_at=time.time(),
        resolved_at=time.time() if result["verification_status"] == "RESOLVED" else None,
        agent_report=result["final_report"],
    )
    db.add(incident_record)

    # Persist Executed Actions to Audit Ledger
    for act in result["actions_executed"]:
        entry = AuditLedger(
            incident_id=inc_id,
            action_type=act["action"],
            target_service=act["target"],
            performed_by="AutoSRE_Agent",
            status=act["status"],
            timestamp=act["timestamp"],
            details=act["details"],
            requires_human_approval=False,
        )
        db.add(entry)

    db.commit()
    db.refresh(incident_record)

    return {
        "message": "Incident detected, diagnosed, and remediated by AutoSRE Agent.",
        "incident_id": inc_id,
        "result": result,
    }

@app.get("/api/audit-logs")
def list_audit_ledger(limit: int = 50, db: Session = Depends(get_db)):
    logs = db.query(AuditLedger).order_by(AuditLedger.timestamp.desc()).limit(limit).all()
    return logs

@app.post("/api/actions/approve")
def approve_action(req: ActionApprovalRequest, db: Session = Depends(get_db)):
    audit = db.query(AuditLedger).filter(AuditLedger.id == req.audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit log entry not found")

    if req.approved:
        audit.status = "APPROVED_BY_HUMAN"
        # Execute the action via cluster tools
        if audit.action_type == "restart_deployment":
            cluster_tools.restart_deployment(audit.target_service)
        audit.details += " | Authorized by human operator."
    else:
        audit.status = "REJECTED_BY_HUMAN"
        audit.details += " | Rejected by human operator."

    db.commit()
    return {"status": audit.status}

# ------------------------------------------------------------------------------
# Mount Dashboard Frontend
# ------------------------------------------------------------------------------
DASHBOARD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../dashboard"))
if os.path.exists(DASHBOARD_DIR):
    app.mount("/", StaticFiles(directory=DASHBOARD_DIR, html=True), name="dashboard")
