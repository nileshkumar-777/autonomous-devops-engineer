import logging
import os
import time
import uuid
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, Field
import httpx
from prometheus_fastapi_instrumentator import Instrumentator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("order-service")

app = FastAPI(
    title="Order Service",
    description="Manages ordering pipeline and checks payment status. Simulates cascading dependency failures.",
    version="1.0.0",
)

Instrumentator().instrument(app).expose(app)

PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://localhost:8002")
NOTIFY_SERVICE_URL = os.getenv("NOTIFY_SERVICE_URL", "http://localhost:8004")

ORDERS_DB: Dict[str, dict] = {}

chaos_state = {
    "latency_ms": 0,
    "error_rate": 0.0,
}

class OrderItem(BaseModel):
    item_id: str
    quantity: int = 1
    unit_price: float

class CreateOrderRequest(BaseModel):
    user_id: str
    items: List[OrderItem]

class ChaosConfig(BaseModel):
    latency_ms: Optional[int] = 0
    error_rate: Optional[float] = 0.0

rate_limiter_state = {
    "enabled": True,
    "max_requests_per_sec": 100,
    "request_history": [],
    "total_throttled": 0,
}

@app.middleware("http")
async def traffic_and_chaos_middleware(request: Request, call_next):
    if request.url.path in ["/health", "/metrics", "/chaos/status", "/chaos/reset", "/ratelimit/status"]:
        return await call_next(request)

    # 1. Rate Limiting & Load Shedding Protection
    if rate_limiter_state["enabled"]:
        now = time.time()
        # Clean timestamps older than 1 second
        rate_limiter_state["request_history"] = [t for t in rate_limiter_state["request_history"] if now - t < 1.0]
        
        if len(rate_limiter_state["request_history"]) >= rate_limiter_state["max_requests_per_sec"]:
            rate_limiter_state["total_throttled"] += 1
            logger.warning("Traffic Surge Throttled: %d requests/sec exceeded max limit of %d. Returning 429.", 
                           len(rate_limiter_state["request_history"]), rate_limiter_state["max_requests_per_sec"])
            return Response(
                content='{"error": "Too Many Requests", "detail": "Traffic surge exceeded capacity. Throttling applied to protect database.", "status": 429}',
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": "2"}
            )
        rate_limiter_state["request_history"].append(now)

    # 2. Chaos Injection Simulation
    if chaos_state["latency_ms"] > 0:
        time.sleep(chaos_state["latency_ms"] / 1000.0)

    if chaos_state["error_rate"] > 0:
        import random
        if random.random() < chaos_state["error_rate"]:
            logger.error("Chaos error in order-service pipeline: 500 triggered on %s", request.url.path)
            return Response(content='{"error": "Simulated Order Pipeline Failure"}', status_code=500, media_type="application/json")

    return await call_next(request)

@app.get("/ratelimit/status")
def get_ratelimit_status():
    now = time.time()
    current_rps = len([t for t in rate_limiter_state["request_history"] if now - t < 1.0])
    return {
        "rate_limiting_enabled": rate_limiter_state["enabled"],
        "current_requests_per_sec": current_rps,
        "max_capacity_per_sec": rate_limiter_state["max_requests_per_sec"],
        "total_requests_throttled": rate_limiter_state["total_throttled"],
        "protection_status": "ACTIVE (HTTP 429 Load Shedding)",
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "order-service",
        "version": "1.0.0",
        "payment_service_url": PAYMENT_SERVICE_URL,
    }

@app.post("/api/v1/orders", status_code=201)
async def create_order(order: CreateOrderRequest):
    order_id = f"ord_{uuid.uuid4().hex[:10]}"
    total_amount = sum(item.quantity * item.unit_price for item in order.items)
    
    logger.info("Received order %s from user %s, total=%.2f", order_id, order.user_id, total_amount)

    # Call payment-service
    payment_status = "PENDING"
    payment_id = None
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            pay_resp = await client.post(
                f"{PAYMENT_SERVICE_URL}/api/v1/payments",
                json={
                    "order_id": order_id,
                    "user_id": order.user_id,
                    "amount": total_amount,
                },
            )
            if pay_resp.status_code == 201:
                pay_data = pay_resp.json()
                payment_id = pay_data.get("payment_id")
                payment_status = "PAID"
                logger.info("Order %s payment approved (payment_id=%s)", order_id, payment_id)
            else:
                payment_status = "PAYMENT_FAILED"
                logger.error("Order %s payment failed: status=%d, body=%s", order_id, pay_resp.status_code, pay_resp.text)
    except httpx.RequestError as exc:
        payment_status = "PAYMENT_UNREACHABLE"
        logger.error("Downstream timeout/network error calling payment-service for order %s: %s", order_id, str(exc))

    record = {
        "order_id": order_id,
        "user_id": order.user_id,
        "items": [item.model_dump() for item in order.items],
        "total_amount": total_amount,
        "payment_status": payment_status,
        "payment_id": payment_id,
        "created_at": time.time(),
    }
    ORDERS_DB[order_id] = record

    if payment_status != "PAID":
        raise HTTPException(
            status_code=502,
            detail=f"Order creation degraded due to downstream payment failure: {payment_status}",
        )

    return record

@app.get("/api/v1/orders")
def list_orders():
    return list(ORDERS_DB.values())

@app.get("/api/v1/orders/{order_id}")
def get_order(order_id: str):
    if order_id not in ORDERS_DB:
        raise HTTPException(status_code=404, detail="Order not found")
    return ORDERS_DB[order_id]

# Chaos injection
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
