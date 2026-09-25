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
