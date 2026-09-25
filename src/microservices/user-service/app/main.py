import logging
import os
import time
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, EmailStr
from prometheus_fastapi_instrumentator import Instrumentator

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("user-service")

app = FastAPI(
    title="User Service",
    description="Manages user profiles and authentication for the Autonomous DevOps testbed.",
    version="1.0.0",
)

# Initialize Prometheus instrumentation
Instrumentator().instrument(app).expose(app)

# In-memory store
USERS_DB: Dict[str, dict] = {
    "usr_101": {"id": "usr_101", "name": "Alice Johnson", "email": "alice@example.com", "tier": "premium"},
    "usr_102": {"id": "usr_102", "name": "Bob Smith", "email": "bob@example.com", "tier": "standard"},
    "usr_103": {"id": "usr_103", "name": "Charlie Davis", "email": "charlie@example.com", "tier": "enterprise"},
}

# Chaos simulation state
chaos_state = {
    "latency_ms": 0,
    "error_rate": 0.0,
    "leak_buffer": [],
}

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    tier: Optional[str] = "standard"

class ChaosConfig(BaseModel):
    latency_ms: Optional[int] = 0
    error_rate: Optional[float] = 0.0
    leak_mb: Optional[int] = 0

@app.middleware("http")
async def chaos_middleware(request: Request, call_next):
    # Skip chaos for health and metrics
    if request.url.path in ["/health", "/metrics", "/chaos/status", "/chaos/reset"]:
        return await call_next(request)

    # Inject artificial latency
    if chaos_state["latency_ms"] > 0:
        time.sleep(chaos_state["latency_ms"] / 1000.0)

    # Inject artificial errors
    if chaos_state["error_rate"] > 0:
        import random
        if random.random() < chaos_state["error_rate"]:
            logger.error("Chaos-induced 500 error triggered on %s", request.url.path)
            return Response(content='{"error": "Simulated Internal Server Error"}', status_code=500, media_type="application/json")

    return await call_next(request)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "user-service",
        "version": "1.0.0",
        "chaos_active": chaos_state["latency_ms"] > 0 or chaos_state["error_rate"] > 0 or len(chaos_state["leak_buffer"]) > 0,
    }

@app.get("/api/v1/users")
def list_users() -> List[dict]:
    logger.info("Listing all registered users (count=%d)", len(USERS_DB))
    return list(USERS_DB.values())

@app.get("/api/v1/users/{user_id}")
def get_user(user_id: str):
    if user_id not in USERS_DB:
        logger.warning("User not found: %s", user_id)
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    logger.info("Retrieved profile for user %s", user_id)
    return USERS_DB[user_id]

@app.post("/api/v1/users", status_code=201)
def create_user(user: UserCreate):
    new_id = f"usr_{len(USERS_DB) + 101}"
    record = {"id": new_id, "name": user.name, "email": user.email, "tier": user.tier}
    USERS_DB[new_id] = record
    logger.info("Created new user: %s (id=%s)", user.name, new_id)
    return record

# ------------------------------------------------------------------------------
# SRE Chaos Injection Endpoints
# ------------------------------------------------------------------------------
@app.post("/chaos/inject")
def inject_chaos(config: ChaosConfig):
    chaos_state["latency_ms"] = config.latency_ms or 0
    chaos_state["error_rate"] = config.error_rate or 0.0
    if config.leak_mb and config.leak_mb > 0:
        # Allocate bytes to simulate memory pressure / OOM risk
        chunk = bytearray(config.leak_mb * 1024 * 1024)
        chaos_state["leak_buffer"].append(chunk)
        logger.warning("Chaos: Leaked %d MB in RAM (Total chunks: %d)", config.leak_mb, len(chaos_state["leak_buffer"]))
    logger.warning("Chaos state updated: latency=%dms, error_rate=%.2f", chaos_state["latency_ms"], chaos_state["error_rate"])
    return {"status": "chaos_configured", "current_state": {"latency_ms": chaos_state["latency_ms"], "error_rate": chaos_state["error_rate"], "leaked_chunks": len(chaos_state["leak_buffer"])}}

@app.post("/chaos/reset")
def reset_chaos():
    chaos_state["latency_ms"] = 0
    chaos_state["error_rate"] = 0.0
    chaos_state["leak_buffer"].clear()
    logger.info("Chaos state completely reset to healthy defaults.")
    return {"status": "chaos_cleared"}

@app.get("/chaos/status")
def get_chaos_status():
    return {
        "latency_ms": chaos_state["latency_ms"],
        "error_rate": chaos_state["error_rate"],
        "leaked_chunks": len(chaos_state["leak_buffer"]),
    }
