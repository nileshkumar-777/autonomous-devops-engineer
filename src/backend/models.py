import time
from sqlalchemy import Column, Integer, String, Float, Text, Boolean
from src.backend.database import Base

class IncidentRecord(Base):
    __tablename__ = "incidents"

    id = Column(String, primary_key=True, index=True)
    service_name = Column(String, index=True)
    alert_name = Column(String)
    severity = Column(String, default="HIGH")
    status = Column(String, default="INVESTIGATING")  # INVESTIGATING, RESOLVED, ESCALATED, PENDING_APPROVAL
    diagnosis = Column(Text, default="")
    confidence = Column(Float, default=0.0)
    created_at = Column(Float, default=time.time)
    resolved_at = Column(Float, nullable=True)
    agent_report = Column(Text, default="")

class AuditLedger(Base):
    __tablename__ = "audit_ledger"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    incident_id = Column(String, index=True)
    action_type = Column(String)
    target_service = Column(String)
    performed_by = Column(String, default="AutoSRE_Agent")
    status = Column(String, default="EXECUTED")  # EXECUTED, BLOCKED, APPROVED, REJECTED
    timestamp = Column(Float, default=time.time)
    details = Column(Text, default="")
    requires_human_approval = Column(Boolean, default=False)

class SystemConnector(Base):
    __tablename__ = "system_connectors"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    system_type = Column(String, nullable=False)  # KUBERNETES, VERCEL, GITHUB, PROMETHEUS, SLACK
    target_endpoint = Column(String, nullable=False)
    auth_type = Column(String, default="BEARER_TOKEN")  # KUBECONFIG, IAM_ROLE, BEARER_TOKEN, WEBHOOK_SECRET
    environment = Column(String, default="PRODUCTION")  # PRODUCTION, STAGING, DEVELOPMENT
    status = Column(String, default="CONNECTED")  # CONNECTED, DEGRADED, DISCONNECTED
    latency_ms = Column(Float, default=25.0)
    last_synced_at = Column(Float, default=time.time)
    auto_remediation_enabled = Column(Boolean, default=True)
    metadata_json = Column(Text, default="{}")
