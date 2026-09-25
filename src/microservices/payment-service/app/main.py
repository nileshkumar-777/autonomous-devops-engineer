import logging
import random
import time
import uuid
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, Field
from prometheus_fastapi_instrumentator import Instrumentator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("payment-service")

app = FastAPI(
    title="Payment Service",
    description="Processes bank/card charges and simulates payment latency/failures for SRE exercises.",
    version="1.0.0",
)

# Prometheus instrumentation
Instrumentator().instrument(app).expose(app)

# In-memory payment ledger
PAYMENTS_DB: Dict[str, dict] = {}

# SRE Chaos state
chaos_state = {
    "latency_ms": 0,
    "error_rate": 0.0,
    "db_connection_pool_exhausted": False,
    "leak_buffer": [],
}

class PaymentRequest(BaseModel):
    order_id: str
    user_id: str
    amount: float = Field(gt=0, description="Amount must be positive")
    currency: str = "USD"
    payment_method: str = "credit_card"

class ChaosConfig(BaseModel):
    latency_ms: Optional[int] = 0
    error_rate: Optional[float] = 0.0
    db_exhaust: Optional[bool] = False
    leak_mb: Optional[int] = 0

@app.middleware("http")
async def chaos_middleware(request: Request, call_next):
    if request.url.path in ["/health", "/metrics", "/chaos/status", "/chaos/reset"]:
        return await call_next(request)

    # 1. Simulate DB pool exhaustion (returns 503 Service Unavailable)
    if chaos_state["db_connection_pool_exhausted"]:
        logger.error("FATAL: Database connection pool exhausted! Unable to acquire connection from pool (timeout 30s).")
        return Response(
            content='{"error": "Database connection pool exhausted", "code": "DB_POOL_TIMEOUT", "service": "payment-service"}',
            status_code=503,
            media_type="application/json"
        )

    # 2. Simulate latency
    if chaos_state["latency_ms"] > 0:
        time.sleep(chaos_state["latency_ms"] / 1000.0)

    # 3. Simulate random error rate
    if chaos_state["error_rate"] > 0:
        if random.random() < chaos_state["error_rate"]:
            logger.error("Payment Gateway timeout or internal error on transaction %s", request.url.path)
            return Response(
                content='{"error": "Payment gateway communication failure", "code": "GATEWAY_TIMEOUT"}',
                status_code=500,
                media_type="application/json"
            )

    return await call_next(request)

@app.get("/health")
def health_check():
    is_degraded = (
        chaos_state["db_connection_pool_exhausted"]
        or chaos_state["latency_ms"] > 2000
        or chaos_state["error_rate"] > 0.5
    )
    return {
        "status": "degraded" if is_degraded else "healthy",
        "service": "payment-service",
        "version": "1.0.0",
        "db_connected": not chaos_state["db_connection_pool_exhausted"],
        "active_chaos": chaos_state,
    }

@app.post("/api/v1/payments", status_code=201)
def process_payment(payment: PaymentRequest):
    logger.info("Initiating payment: order_id=%s, amount=%.2f %s", payment.order_id, payment.amount, payment.currency)
    
    payment_id = f"pay_{uuid.uuid4().hex[:12]}"
    record = {
        "payment_id": payment_id,
        "order_id": payment.order_id,
        "user_id": payment.user_id,
        "amount": payment.amount,
        "currency": payment.currency,
        "status": "SUCCESS",
        "created_at": time.time(),
    }
    PAYMENTS_DB[payment_id] = record
    logger.info("Payment %s processed successfully for order %s", payment_id, payment.order_id)
    return record

@app.get("/api/v1/payments/{payment_id}")
def get_payment(payment_id: str):
    if payment_id not in PAYMENTS_DB:
        logger.warning("Payment record not found: %s", payment_id)
        raise HTTPException(status_code=404, detail="Payment record not found")
    return PAYMENTS_DB[payment_id]

# ------------------------------------------------------------------------------
# SRE Chaos Injection
# ------------------------------------------------------------------------------
@app.post("/chaos/inject")
def inject_chaos(config: ChaosConfig):
    chaos_state["latency_ms"] = config.latency_ms or 0
    chaos_state["error_rate"] = config.error_rate or 0.0
    chaos_state["db_connection_pool_exhausted"] = bool(config.db_exhaust)
    if config.leak_mb and config.leak_mb > 0:
        chunk = bytearray(config.leak_mb * 1024 * 1024)
        chaos_state["leak_buffer"].append(chunk)
        logger.warning("Allocated %d MB memory leak (Total chunks: %d)", config.leak_mb, len(chaos_state["leak_buffer"]))
    
    logger.warning("Chaos applied: latency=%dms, error_rate=%.2f, db_exhaust=%s",
                   chaos_state["latency_ms"], chaos_state["error_rate"], chaos_state["db_connection_pool_exhausted"])
    return {"status": "chaos_injected", "current_state": chaos_state}

@app.post("/chaos/reset")
def reset_chaos():
    chaos_state["latency_ms"] = 0
    chaos_state["error_rate"] = 0.0
    chaos_state["db_connection_pool_exhausted"] = False
    chaos_state["leak_buffer"].clear()
    logger.info("Payment service chaos cleared. System restored to baseline healthy operation.")
    return {"status": "chaos_cleared"}

@app.get("/chaos/status")
def get_chaos_status():
    return chaos_state
