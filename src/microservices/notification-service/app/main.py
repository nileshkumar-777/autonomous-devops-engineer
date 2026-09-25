import logging
import time
import uuid
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, EmailStr
from prometheus_fastapi_instrumentator import Instrumentator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("notification-service")

app = FastAPI(
    title="Notification Service",
    description="Dispatches email, SMS, and webhook alerts for orders and SRE incident notifications.",
    version="1.0.0",
)

Instrumentator().instrument(app).expose(app)

NOTIFICATIONS_LOG: List[dict] = []

chaos_state = {
    "latency_ms": 0,
    "error_rate": 0.0,
}

class NotificationRequest(BaseModel):
    recipient: str
    channel: str = "email"  # email, sms, slack, webhook
    subject: str
    body: str

class ChaosConfig(BaseModel):
    latency_ms: Optional[int] = 0
    error_rate: Optional[float] = 0.0

@app.middleware("http")
async def chaos_middleware(request: Request, call_next):
    if request.url.path in ["/health", "/metrics", "/chaos/status", "/chaos/reset"]:
        return await call_next(request)

    if chaos_state["latency_ms"] > 0:
        time.sleep(chaos_state["latency_ms"] / 1000.0)

    if chaos_state["error_rate"] > 0:
        import random
        if random.random() < chaos_state["error_rate"]:
            logger.error("Notification dispatch failure: Simulated 500 triggered on %s", request.url.path)
            return Response(content='{"error": "Notification Dispatcher Failure"}', status_code=500, media_type="application/json")

    return await call_next(request)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "notification-service",
        "version": "1.0.0",
        "total_dispatched": len(NOTIFICATIONS_LOG),
    }

@app.post("/api/v1/notify", status_code=202)
def send_notification(req: NotificationRequest):
    notif_id = f"ntf_{uuid.uuid4().hex[:10]}"
    record = {
        "id": notif_id,
        "recipient": req.recipient,
        "channel": req.channel,
        "subject": req.subject,
        "status": "SENT",
        "timestamp": time.time(),
    }
    NOTIFICATIONS_LOG.append(record)
    logger.info("Dispatched %s notification to %s (id=%s)", req.channel, req.recipient, notif_id)
    return {"status": "accepted", "notification_id": notif_id}

@app.get("/api/v1/notifications")
def list_notifications(limit: int = 50):
    return NOTIFICATIONS_LOG[-limit:]

@app.post("/chaos/inject")
def inject_chaos(config: ChaosConfig):
    chaos_state["latency_ms"] = config.latency_ms or 0
    chaos_state["error_rate"] = config.error_rate or 0.0
    return {"status": "chaos_injected", "current_state": chaos_state}

@app.post("/chaos/reset")
def reset_chaos():
    chaos_state["latency_ms"] = 0
    chaos_state["error_rate"] = 0.0
    return {"status": "chaos_cleared"}

@app.get("/chaos/status")
def get_chaos_status():
    return chaos_state
