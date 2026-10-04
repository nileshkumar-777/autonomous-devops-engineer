import json
import logging
import os
import random
import time
from typing import Dict, List, Optional, Any
import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from prometheus_fastapi_instrumentator import Instrumentator

from collections import deque

LOG_BUFFER = deque(maxlen=200)

class InMemoryLogHandler(logging.Handler):
    def emit(self, record):
        try:
            msg = self.format(record)
            LOG_BUFFER.append(msg)
        except Exception:
            pass

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [restaurant-cafe-service] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("restaurant-cafe-service")
_mem_handler = InMemoryLogHandler()
_mem_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] [restaurant-cafe-service] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
logger.addHandler(_mem_handler)

app = FastAPI(
    title="Bella Vista Artisan Cafe & Bistro (Target Project)",
    description="Authentic Cafe & Restaurant Web Application connected to AutoSRE Control Plane for autonomous incident detection and self-healing.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/logs")
@app.get("/logs")
def get_service_runtime_logs(tail: int = 50):
    """Exposes real-time streaming runtime logs for AutoSRE log scraping & ML anomaly detection."""
    lines = list(LOG_BUFFER)
    return {"service": "restaurant-cafe-service", "total": len(lines), "logs": lines[-tail:] if lines else ["Initial system heartbeat operational"]}


# Prometheus instrumentation
Instrumentator().instrument(app).expose(app)

# ------------------------------------------------------------------------------
# In-Memory Menu Catalog & Inventory Database
# ------------------------------------------------------------------------------
INVENTORY_DB: Dict[str, dict] = {
    # Backward-compatible SKU codes for existing integration test suite
    "sku_1001": {
        "sku": "sku_1001",
        "name": "Ethiopian Yirgacheffe Single-Origin Beans (250g)",
        "category": "Roasts & Beans",
        "price": 18.50,
        "stock": 45,
        "reserved": 0,
        "prep_time": "Ready to Ship",
        "description": "Floral jasmine, bergamot, and sweet citrus notes. Light roasted at altitude.",
        "badge": "Single Origin",
        "icon": "fa-seedling"
    },
    "sku_1002": {
        "sku": "sku_1002",
        "name": "Bella Vista House Blend Dark Roast (500g)",
        "category": "Roasts & Beans",
        "price": 22.00,
        "stock": 80,
        "reserved": 0,
        "prep_time": "Ready to Ship",
        "description": "Rich dark chocolate, roasted almond, and caramel notes with full body.",
        "badge": "House Blend",
        "icon": "fa-fire"
    },
    "sku_1003": {
        "sku": "sku_1003",
        "name": "Cascara Nitro Cold Brew Keg (2L)",
        "category": "Roasts & Beans",
        "price": 38.00,
        "stock": 15,
        "reserved": 0,
        "prep_time": "Ready to Ship",
        "description": "Steeped for 24 hours in glacial cold water. Rich berry sweetness.",
        "badge": "Nitro Reserve",
        "icon": "fa-wine-bottle"
    },
    "sku_1004": {
        "sku": "sku_1004",
        "name": "Ceremonial Grade Uji Matcha (100g)",
        "category": "Roasts & Beans",
        "price": 29.99,
        "stock": 30,
        "reserved": 0,
        "prep_time": "Ready to Ship",
        "description": "First-harvest stone-ground Japanese green tea matcha from Kyoto.",
        "badge": "Ceremonial",
        "icon": "fa-leaf"
    },

    # Cafe & Restaurant Handcrafted Menu Items
    "menu_espresso": {
        "sku": "menu_espresso",
        "name": "Signature Double Espresso Romano",
        "category": "Artisanal Coffee",
        "price": 4.50,
        "stock": 200,
        "reserved": 0,
        "prep_time": "3 mins",
        "description": "Double ristretto extraction pulled over candied Sorrento lemon peel.",
        "badge": "Classic",
        "icon": "fa-mug-hot"
    },
    "menu_cappuccino": {
        "sku": "menu_cappuccino",
        "name": "Velvet Truffle Crema Cappuccino",
        "category": "Artisanal Coffee",
        "price": 6.25,
        "stock": 150,
        "reserved": 0,
        "prep_time": "4 mins",
        "description": "Micro-foam oat milk dusted with organic Dutch cacao and vanilla crema.",
        "badge": "Top Rated",
        "icon": "fa-mug-saucer"
    },
    "menu_nitro": {
        "sku": "menu_nitro",
        "name": "Salted Caramel Cold Brew Cascade",
        "category": "Artisanal Coffee",
        "price": 6.75,
        "stock": 120,
        "reserved": 0,
        "prep_time": "2 mins",
        "description": "Silky nitro cold brew layered over house salted caramel and whipped cold foam.",
        "badge": "Trending",
        "icon": "fa-glass-water"
    },
    "menu_croissant": {
        "sku": "menu_croissant",
        "name": "Almond Frangipane Brioche Croissant",
        "category": "Bakery & Pastries",
        "price": 5.25,
        "stock": 40,
        "reserved": 0,
        "prep_time": "Fresh Warm",
        "description": "Double-baked buttery croissant filled with fragrant almond frangipane.",
        "badge": "Baked Fresh",
        "icon": "fa-bread-slice"
    },
    "menu_cinnamon": {
        "sku": "menu_cinnamon",
        "name": "Cardamom & Brown Butter Sourdough Swirl",
        "category": "Bakery & Pastries",
        "price": 5.50,
        "stock": 35,
        "reserved": 0,
        "prep_time": "Fresh Warm",
        "description": "Wild sourdough fermented for 36 hours, glazed with vanilla mascarpone.",
        "badge": "Signature",
        "icon": "fa-cookie"
    },
    "menu_tartine": {
        "sku": "menu_tartine",
        "name": "Avocado & Poached Egg Truffle Tartine",
        "category": "All-Day Brunch",
        "price": 14.50,
        "stock": 50,
        "reserved": 0,
        "prep_time": "10 mins",
        "description": "Toasted sourdough with smashed Hass avocado, organic poached eggs, and microgreens.",
        "badge": "Organic",
        "icon": "fa-egg"
    },
    "menu_benedict": {
        "sku": "menu_benedict",
        "name": "Smoked Atlantic Salmon Benedict",
        "category": "All-Day Brunch",
        "price": 17.50,
        "stock": 35,
        "reserved": 0,
        "prep_time": "12 mins",
        "description": "Brioche bun, cold-smoked salmon, organic poached eggs, and yuzu hollandaise.",
        "badge": "Chef Special",
        "icon": "fa-utensils"
    },
    "menu_flatbread": {
        "sku": "menu_flatbread",
        "name": "Wood-Fired Burrata & Basil Flatbread",
        "category": "Bistro Mains",
        "price": 16.50,
        "stock": 30,
        "reserved": 0,
        "prep_time": "14 mins",
        "description": "San Marzano tomatoes, fresh Pugliese burrata, fragrant basil, and virgin olive oil.",
        "badge": "Wood Fired",
        "icon": "fa-pizza-slice"
    },
    "menu_panini": {
        "sku": "menu_panini",
        "name": "Tuscan Prosciutto & Fontina Panini",
        "category": "Bistro Mains",
        "price": 15.00,
        "stock": 40,
        "reserved": 0,
        "prep_time": "8 mins",
        "description": "Aged Prosciutto di Parma, melted fontina cheese, wild arugula, and fig glaze.",
        "badge": "Gourmet",
        "icon": "fa-burger"
    },
    "menu_tiramisu": {
        "sku": "menu_tiramisu",
        "name": "Traditional Espresso Tiramisu Classico",
        "category": "Desserts",
        "price": 8.50,
        "stock": 45,
        "reserved": 0,
        "prep_time": "Chilled",
        "description": "Savoiardi ladyfingers steeped in espresso and Marsala wine with velvety mascarpone.",
        "badge": "Artisan Made",
        "icon": "fa-cake-candles"
    },
}

# Live Orders & Table Reservations Store
ORDERS_STORE: List[dict] = []
RESERVATIONS_STORE: List[dict] = []

# Chaos & Failure Simulation State
chaos_state = {
    "latency_ms": 0,
    "error_rate": 0.0,
    "db_pool_exhausted": False,
    "cpu_spike": False,
    "memory_leak_mb": 0,
    "leak_buffer": [],
}

class ReserveItemRequest(BaseModel):
    sku: str
    quantity: int = Field(gt=0, description="Quantity must be greater than zero")
    order_id: str

class OrderCreateRequest(BaseModel):
    customer_name: str
    order_type: str = "dine_in"  # dine_in, takeout, delivery
    table_number: Optional[str] = "Table 4"
    items: List[Dict[str, Any]]  # [{"sku": "menu_espresso", "quantity": 2}]
    special_notes: Optional[str] = ""

class ReservationRequest(BaseModel):
    customer_name: str
    email: str
    phone: str
    guests: int = Field(gt=0, le=20)
    reservation_date: str
    reservation_time: str
    seating_preference: Optional[str] = "Garden Patio"

class ChaosConfig(BaseModel):
    latency_ms: Optional[int] = 0
    error_rate: Optional[float] = 0.0
    db_exhaust: Optional[bool] = False
    cpu_spike: Optional[bool] = False
    leak_mb: Optional[int] = 0

# ------------------------------------------------------------------------------
# HTTP Chaos Middleware
# ------------------------------------------------------------------------------
@app.middleware("http")
async def chaos_middleware(request: Request, call_next):
    # Exclude system and UI endpoints from chaos injection
    if request.url.path in [
        "/",
        "/health",
        "/metrics",
        "/docs",
        "/openapi.json",
        "/chaos/status",
        "/chaos/reset",
        "/remediate/restart",
        "/remediate/scale",
        "/api/trigger-incident-to-autosre",
    ]:
        return await call_next(request)

    # 1. DB Pool Exhaustion simulation (HTTP 503)
    if chaos_state["db_pool_exhausted"]:
        logger.error("FATAL: PostgreSQL Connection Pool Exhausted! POS and Reservation worker threads timed out.")
        return Response(
            content=json.dumps({
                "error": "Database connection pool exhausted",
                "code": "DB_POOL_TIMEOUT",
                "service": "restaurant-cafe-service",
                "detail": "Failed to acquire database connection within 5000ms. Orders & reservations blocked."
            }),
            status_code=503,
            media_type="application/json",
        )

    # 2. Artificial latency simulation
    if chaos_state["latency_ms"] > 0:
        time.sleep(chaos_state["latency_ms"] / 1000.0)

    # 3. Random error simulation
    if chaos_state["error_rate"] > 0:
        if random.random() < chaos_state["error_rate"]:
            logger.error("Internal service error triggered on route %s (Kitchen POS failure)", request.url.path)
            return Response(
                content=json.dumps({
                    "error": "Internal Server Error in Kitchen POS Worker",
                    "service": "restaurant-cafe-service",
                    "code": "INTERNAL_SERVER_ERROR"
                }),
                status_code=500,
                media_type="application/json",
            )

    return await call_next(request)

# ------------------------------------------------------------------------------
# Web Dashboard: Authentic Artisan Cafe & Bistro Website
# ------------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def index_page():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bella Vista Artisan Cafe & Bistro</title>
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,600&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        :root {
            --bg-body: #0F0D0B;
            --surface: #181512;
            --surface-card: #201B17;
            --surface-hover: #2A241F;
            --border: rgba(230, 180, 120, 0.12);
            --border-highlight: rgba(217, 119, 6, 0.4);
            
            --amber: #F59E0B;
            --amber-gold: #D97706;
            --espresso: #3E2723;
            --cream: #FEF3C7;
            --emerald: #10B981;
            --rose: #EF4444;
            --cyan: #06B6D4;
            --indigo: #6366F1;
            
            --text-primary: #FDFBF7;
            --text-secondary: #D1C7BD;
            --text-muted: #9C8F80;
            
            --font-sans: 'Plus Jakarta Sans', sans-serif;
            --font-serif: 'Playfair Display', serif;
            --font-mono: 'JetBrains Mono', monospace;
            --shadow-subtle: 0 4px 20px rgba(0, 0, 0, 0.35);
            --shadow-glow: 0 0 25px rgba(245, 158, 11, 0.2);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        html { scroll-behavior: smooth; }
        body {
            background-color: var(--bg-body);
            background-image: 
                radial-gradient(circle at 15% 15%, rgba(217, 119, 6, 0.08) 0%, transparent 45%),
                radial-gradient(circle at 85% 75%, rgba(245, 158, 11, 0.05) 0%, transparent 45%);
            color: var(--text-primary);
            font-family: var(--font-sans);
            min-height: 100vh;
            line-height: 1.5;
        }

        /* Top Announcement Strip */
        .top-strip {
            background: linear-gradient(90deg, #2D1B0D, #45260E, #2D1B0D);
            border-bottom: 1px solid var(--border);
            padding: 8px 16px;
            font-size: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: var(--cream);
            flex-wrap: wrap;
            gap: 8px;
        }
        .top-strip-left { display: flex; align-items: center; gap: 12px; }
        .top-strip-right { display: flex; align-items: center; gap: 16px; font-family: var(--font-mono); font-size: 11.5px; }

        /* Navigation Bar */
        .navbar {
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(16px);
            background: rgba(15, 13, 11, 0.88);
            border-bottom: 1px solid var(--border);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .brand {
            display: flex;
            align-items: center;
            gap: 12px;
            text-decoration: none;
            color: inherit;
        }
        .brand-logo {
            width: 44px;
            height: 44px;
            border-radius: 12px;
            background: linear-gradient(135deg, #D97706, #B45309);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #FFF;
            font-size: 22px;
            box-shadow: 0 4px 15px rgba(217, 119, 6, 0.35);
        }
        .brand-text h1 {
            font-family: var(--font-serif);
            font-size: 21px;
            font-weight: 700;
            letter-spacing: -0.3px;
            color: #FFF;
        }
        .brand-text p {
            font-size: 11px;
            color: var(--amber);
            font-family: var(--font-sans);
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
        }

        .nav-links {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        .nav-link {
            color: var(--text-secondary);
            text-decoration: none;
            font-size: 14px;
            font-weight: 500;
            transition: color 0.2s;
        }
        .nav-link:hover { color: var(--amber); }

        .btn {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 9px 18px;
            border-radius: 9999px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            border: 1px solid transparent;
            text-decoration: none;
            transition: all 0.2s ease;
        }
        .btn-primary {
            background: linear-gradient(135deg, #F59E0B, #D97706);
            color: #0F0D0B;
            box-shadow: 0 4px 14px rgba(245, 158, 11, 0.3);
        }
        .btn-primary:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);
        }
        .btn-outline {
            background: transparent;
            border-color: var(--border);
            color: var(--text-primary);
        }
        .btn-outline:hover {
            background: var(--surface-hover);
            border-color: var(--amber);
        }
        .btn-danger {
            background: rgba(239, 68, 68, 0.15);
            border-color: rgba(239, 68, 68, 0.35);
            color: var(--rose);
        }
        .btn-danger:hover {
            background: var(--rose);
            color: #FFF;
        }
        .btn-success {
            background: rgba(16, 185, 129, 0.15);
            border-color: rgba(16, 185, 129, 0.35);
            color: var(--emerald);
        }
        .btn-success:hover {
            background: var(--emerald);
            color: #FFF;
        }

        .cart-trigger-btn {
            position: relative;
            background: var(--surface-card);
            border: 1px solid var(--border);
            color: var(--cream);
            padding: 9px 16px;
            border-radius: 9999px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .cart-trigger-btn:hover { border-color: var(--amber); }
        .cart-count-badge {
            background: var(--amber);
            color: #000;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            font-weight: 800;
        }

        /* Hero Showcase */
        .hero {
            padding: 4.5rem 2rem 3rem;
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 1.2fr 0.8fr;
            gap: 40px;
            align-items: center;
        }
        @media (max-width: 900px) {
            .hero { grid-template-columns: 1fr; padding-top: 2rem; }
        }
        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(245, 158, 11, 0.12);
            border: 1px solid rgba(245, 158, 11, 0.25);
            padding: 6px 14px;
            border-radius: 9999px;
            color: var(--amber);
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 1.2rem;
        }
        .hero-title {
            font-family: var(--font-serif);
            font-size: 46px;
            line-height: 1.15;
            font-weight: 700;
            margin-bottom: 1.2rem;
            color: #FFF;
        }
        .hero-title span {
            color: var(--amber);
            font-style: italic;
        }
        .hero-desc {
            font-size: 16px;
            color: var(--text-secondary);
            margin-bottom: 2rem;
            max-width: 540px;
            line-height: 1.6;
        }
        .hero-actions {
            display: flex;
            gap: 14px;
            flex-wrap: wrap;
        }

        .hero-card {
            background: linear-gradient(145deg, var(--surface-card), #16120E);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 2rem;
            box-shadow: var(--shadow-subtle);
            position: relative;
            overflow: hidden;
        }
        .hero-card::after {
            content: '';
            position: absolute;
            top: -50px;
            right: -50px;
            width: 150px;
            height: 150px;
            background: radial-gradient(circle, rgba(245, 158, 11, 0.18), transparent 70%);
            border-radius: 50%;
        }
        .hero-card h3 {
            font-family: var(--font-serif);
            font-size: 20px;
            margin-bottom: 8px;
        }
        .hero-card p {
            font-size: 13px;
            color: var(--text-muted);
            margin-bottom: 1.5rem;
        }
        .hero-stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 14px;
        }
        .hero-stat-box {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 14px;
        }
        .hero-stat-num {
            font-size: 22px;
            font-weight: 800;
            color: var(--amber);
            font-family: var(--font-mono);
        }
        .hero-stat-label {
            font-size: 11px;
            color: var(--text-muted);
            text-transform: uppercase;
        }

        /* Menu Section */
        .section-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 3rem 2rem;
        }
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            margin-bottom: 2rem;
            flex-wrap: wrap;
            gap: 16px;
        }
        .section-header h2 {
            font-family: var(--font-serif);
            font-size: 32px;
            color: #FFF;
        }
        .section-header p {
            color: var(--text-muted);
            font-size: 14px;
        }

        .category-tabs {
            display: flex;
            gap: 10px;
            overflow-x: auto;
            padding-bottom: 8px;
            margin-bottom: 2rem;
            scrollbar-width: none;
        }
        .category-tab-btn {
            background: var(--surface-card);
            border: 1px solid var(--border);
            color: var(--text-secondary);
            padding: 8px 16px;
            border-radius: 9999px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.2s;
        }
        .category-tab-btn:hover { border-color: var(--amber); color: #FFF; }
        .category-tab-btn.active {
            background: var(--amber);
            color: #0F0D0B;
            border-color: var(--amber);
            font-weight: 700;
        }

        .menu-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(270px, 1fr));
            gap: 20px;
        }
        .menu-card {
            background: var(--surface-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1.4rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
        }
        .menu-card:hover {
            transform: translateY(-3px);
            border-color: var(--border-highlight);
            box-shadow: 0 8px 24px rgba(0,0,0,0.4);
        }
        .menu-card-top {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
        }
        .menu-item-icon {
            width: 40px;
            height: 40px;
            border-radius: 10px;
            background: rgba(245, 158, 11, 0.12);
            color: var(--amber);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
        }
        .badge-pill {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid var(--border);
            padding: 3px 8px;
            border-radius: 9999px;
            font-size: 10px;
            font-weight: 700;
            color: var(--cream);
            text-transform: uppercase;
        }
        .menu-card h4 {
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 6px;
            color: #FFF;
        }
        .menu-card .desc {
            font-size: 12.5px;
            color: var(--text-muted);
            line-height: 1.5;
            margin-bottom: 1rem;
            flex-grow: 1;
        }
        .menu-card-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 12px;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
        }
        .price-tag {
            font-size: 20px;
            font-weight: 800;
            color: var(--amber);
            font-family: var(--font-mono);
        }
        .btn-add-tray {
            background: var(--surface-hover);
            border: 1px solid var(--border);
            color: var(--text-primary);
            padding: 7px 14px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn-add-tray:hover {
            background: var(--amber);
            color: #000;
            border-color: var(--amber);
        }

        /* Table Reservation Form */
        .reservation-box {
            background: linear-gradient(135deg, #1C1712, #231B15);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 2.5rem;
            margin-top: 3rem;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }
        @media (max-width: 800px) {
            .reservation-box { grid-template-columns: 1fr; padding: 1.5rem; }
        }
        .form-group {
            margin-bottom: 14px;
        }
        .form-group label {
            display: block;
            font-size: 12px;
            font-weight: 600;
            color: var(--text-secondary);
            margin-bottom: 6px;
        }
        .form-input, .form-select {
            width: 100%;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 10px 12px;
            color: #FFF;
            font-family: var(--font-sans);
            font-size: 13px;
            outline: none;
            transition: border-color 0.2s;
        }
        .form-input:focus, .form-select:focus {
            border-color: var(--amber);
        }

        /* Shopping Tray Drawer */
        .cart-drawer-overlay {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(4px);
            z-index: 200;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s;
        }
        .cart-drawer-overlay.open {
            opacity: 1;
            pointer-events: auto;
        }
        .cart-drawer {
            position: fixed;
            top: 0; right: -420px; bottom: 0;
            width: 400px;
            max-width: 90vw;
            background: #14110E;
            border-left: 1px solid var(--border);
            z-index: 210;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            transition: right 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            box-shadow: -10px 0 30px rgba(0, 0, 0, 0.6);
        }
        .cart-drawer.open { right: 0; }
        .cart-drawer-head {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--border);
            margin-bottom: 1rem;
        }
        .cart-drawer-head h3 { font-family: var(--font-serif); font-size: 18px; }
        .cart-items-list {
            flex-grow: 1;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .cart-item-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--surface-card);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 10px;
        }
        .cart-item-info h5 { font-size: 13px; font-weight: 600; margin-bottom: 2px; }
        .cart-item-info span { font-size: 12px; color: var(--amber); font-family: var(--font-mono); font-weight: 700; }
        .cart-qty-ctrl {
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .qty-btn {
            width: 24px;
            height: 24px;
            border-radius: 6px;
            border: 1px solid var(--border);
            background: var(--surface);
            color: #FFF;
            cursor: pointer;
            font-size: 12px;
        }
        .cart-drawer-foot {
            padding-top: 1rem;
            border-top: 1px solid var(--border);
            margin-top: 1rem;
        }
        .cart-total-row {
            display: flex;
            justify-content: space-between;
            font-size: 14px;
            margin-bottom: 6px;
            color: var(--text-secondary);
        }
        .cart-grand-total {
            font-size: 18px;
            font-weight: 800;
            color: #FFF;
            margin-top: 8px;
            margin-bottom: 14px;
            display: flex;
            justify-content: space-between;
        }

        /* Order Checkout Modal */
        .modal-overlay {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(6px);
            z-index: 300;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 1rem;
        }
        .modal-overlay.hidden { display: none; }
        .modal-card {
            background: #17130F;
            border: 1px solid var(--border);
            border-radius: 18px;
            width: 100%;
            max-width: 520px;
            padding: 2rem;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.7);
        }

        /* FLOATING SRE CHAOS CONTROL DOCK (FOR TESTING INCIDENT CASCADE) */
        .sre-chaos-dock {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 150;
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 10px;
        }
        .sre-dock-toggle {
            background: linear-gradient(135deg, #1E1B18, #2A241F);
            border: 1px solid var(--border-highlight);
            color: var(--amber);
            padding: 10px 18px;
            border-radius: 9999px;
            font-size: 12.5px;
            font-weight: 700;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
            transition: all 0.2s;
        }
        .sre-dock-toggle:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 25px rgba(217, 119, 6, 0.3);
        }
        .sre-chaos-panel {
            width: 380px;
            max-width: 90vw;
            background: #14110E;
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1.2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8);
            display: none;
        }
        .sre-chaos-panel.open { display: block; }
        .sre-panel-head {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid var(--border);
        }
        .sre-panel-head h4 {
            font-size: 13px;
            font-weight: 800;
            color: #FFF;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .chaos-btn-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            margin-bottom: 10px;
        }
        .chaos-action-btn {
            background: var(--surface-card);
            border: 1px solid var(--border);
            color: var(--text-primary);
            padding: 8px 10px;
            border-radius: 8px;
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
            text-align: left;
            transition: all 0.2s;
        }
        .chaos-action-btn:hover {
            background: var(--surface-hover);
            border-color: var(--rose);
            color: var(--rose);
        }
        .chaos-action-btn.active {
            border-color: var(--rose);
            background: rgba(239, 68, 68, 0.15);
            color: var(--rose);
        }
        .sre-log-console {
            background: #090807;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 8px;
            font-family: var(--font-mono);
            font-size: 11px;
            color: #FED7AA;
            max-height: 120px;
            overflow-y: auto;
            margin-top: 10px;
        }

        /* Order Feedback Banner */
        .toast-msg {
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 500;
            background: #231C16;
            border: 1px solid var(--amber);
            border-radius: 9999px;
            padding: 10px 22px;
            color: #FFF;
            font-size: 13px;
            font-weight: 600;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .toast-msg.hidden { display: none; }
        .toast-msg.error {
            border-color: var(--rose);
            background: #2A1215;
            color: #FECACA;
        }
    </style>
</head>
<body>

    <!-- Top Announcement Strip -->
    <div class="top-strip">
        <div class="top-strip-left">
            <span style="color: var(--amber);"><i class="fa-solid fa-mug-hot"></i></span>
            <span>Welcome to Bella Vista Cafe & Bistro — Roasting Daily on Artisan Hearth</span>
        </div>
        <div class="top-strip-right">
            <span><i class="fa-regular fa-clock"></i> 7:00 AM – 10:00 PM</span>
            <span id="service-health-indicator" style="color: var(--emerald); font-weight: 700;">
                <i class="fa-solid fa-circle" style="font-size: 8px;"></i> POS ONLINE (:8010)
            </span>
            <a href="http://127.0.0.1:8000" target="_blank" style="color: var(--amber); text-decoration: none;">
                <i class="fa-solid fa-bolt"></i> AutoSRE Console (:8000)
            </a>
        </div>
    </div>

    <!-- Navigation Bar -->
    <nav class="navbar">
        <a href="#" class="brand">
            <div class="brand-logo"><i class="fa-solid fa-mug-saucer"></i></div>
            <div class="brand-text">
                <h1>Bella Vista</h1>
                <p>Artisan Cafe & Trattoria</p>
            </div>
        </a>

        <div class="nav-links">
            <a href="#menu" class="nav-link">Menu & Roasts</a>
            <a href="#reservations" class="nav-link">Table Reservations</a>
            <a href="#story" class="nav-link">Our Heritage</a>
            <button class="cart-trigger-btn" onclick="toggleCartDrawer()">
                <i class="fa-solid fa-bag-shopping" style="color: var(--amber);"></i>
                <span>Tray</span>
                <span class="cart-count-badge" id="cart-item-count">0</span>
            </button>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero">
        <div>
            <div class="hero-badge">
                <i class="fa-solid fa-award"></i>
                <span>Voted Best Artisan Roastery & Brunch 2026</span>
            </div>
            <h1 class="hero-title">
                Handcrafted Espresso & <span>Farm-to-Table</span> Bistro Dining
            </h1>
            <p class="hero-desc">
                From slow single-origin Ethiopian cold brews to wood-fired Pugliese burrata flatbreads, every plate is crafted with obsession for taste and craft.
            </p>
            <div class="hero-actions">
                <a href="#menu" class="btn btn-primary">
                    <i class="fa-solid fa-utensils"></i> Explore Full Menu
                </a>
                <a href="#reservations" class="btn btn-outline">
                    <i class="fa-regular fa-calendar-check"></i> Book a Table
                </a>
            </div>
        </div>

        <div class="hero-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <span class="badge-pill" style="background: rgba(245, 158, 11, 0.15); color: var(--amber);">TODAY'S SPECIALTY</span>
                <span style="font-family: var(--font-mono); font-size: 11px; color: var(--emerald);">LIVE KITCHEN DISPATCH</span>
            </div>
            <h3>Slow-Fermented Sourdough & Truffle Roasts</h3>
            <p>Every morning at 5:00 AM, our bakers fire up the hearth with natural levain and cold-churned Normandy butter.</p>
            
            <div class="hero-stats">
                <div class="hero-stat-box">
                    <div class="hero-stat-num">4.9 ★</div>
                    <div class="hero-stat-label">Guest Rating</div>
                </div>
                <div class="hero-stat-box">
                    <div class="hero-stat-num">12 mins</div>
                    <div class="hero-stat-label">Avg Prep Time</div>
                </div>
                <div class="hero-stat-box">
                    <div class="hero-stat-num">100%</div>
                    <div class="hero-stat-label">Fair Trade Roasts</div>
                </div>
                <div class="hero-stat-box">
                    <div class="hero-stat-num" id="live-stock-count">14 items</div>
                    <div class="hero-stat-label">Available Today</div>
                </div>
            </div>
        </div>
    </section>

    <!-- Menu & Ordering Section -->
    <section class="section-container" id="menu">
        <div class="section-header">
            <div>
                <h2>Artisanal Menu & Roasts</h2>
                <p>Curated dishes made with seasonal ingredients and single-estate coffee beans.</p>
            </div>
            <button class="btn btn-outline" onclick="fetchMenu()">
                <i class="fa-solid fa-arrows-rotate"></i> Refresh Availability
            </button>
        </div>

        <!-- Category Filter Tabs -->
        <div class="category-tabs" id="category-tabs-container">
            <button class="category-tab-btn active" onclick="filterCategory('ALL')">All Dishes & Roasts</button>
            <button class="category-tab-btn" onclick="filterCategory('Artisanal Coffee')">☕ Artisanal Coffee</button>
            <button class="category-tab-btn" onclick="filterCategory('Bakery & Pastries')">🥐 Bakery & Pastries</button>
            <button class="category-tab-btn" onclick="filterCategory('All-Day Brunch')">🍳 All-Day Brunch</button>
            <button class="category-tab-btn" onclick="filterCategory('Bistro Mains')">🍕 Bistro Mains</button>
            <button class="category-tab-btn" onclick="filterCategory('Desserts')">🍰 Desserts</button>
            <button class="category-tab-btn" onclick="filterCategory('Roasts & Beans')">📦 Packaged Roasts</button>
        </div>

        <!-- Menu Grid -->
        <div class="menu-grid" id="menu-items-grid">
            <!-- Dynamically populated via JavaScript -->
        </div>
    </section>

    <!-- Table Reservations Section -->
    <section class="section-container" id="reservations">
        <div class="reservation-box">
            <div>
                <div class="hero-badge" style="margin-bottom: 0.8rem;">
                    <i class="fa-regular fa-clock"></i> Reservations
                </div>
                <h2 style="font-family: var(--font-serif); font-size: 28px; margin-bottom: 12px; color: #FFF;">
                    Reserve Your Table at Bella Vista
                </h2>
                <p style="color: var(--text-secondary); font-size: 13.5px; line-height: 1.6; margin-bottom: 1.5rem;">
                    Whether you are planning an intimate brunch on our botanical garden patio or an evening tasting dinner with friends, we welcome you.
                </p>
                <div style="display: flex; flex-direction: column; gap: 10px; font-size: 13px; color: var(--text-muted);">
                    <div><i class="fa-solid fa-location-dot" style="color: var(--amber); width: 20px;"></i> 442 Artisan Blvd, Suite 10, Downtown</div>
                    <div><i class="fa-solid fa-phone" style="color: var(--amber); width: 20px;"></i> (555) 234-CAFE</div>
                    <div><i class="fa-solid fa-envelope" style="color: var(--amber); width: 20px;"></i> reservations@bellavistacafe.com</div>
                </div>
            </div>

            <div>
                <form id="reservation-form" onsubmit="handleReservationSubmit(event)">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                        <div class="form-group">
                            <label>Full Name</label>
                            <input type="text" id="res-name" class="form-input" required placeholder="Elena Vance">
                        </div>
                        <div class="form-group">
                            <label>Party Size</label>
                            <select id="res-guests" class="form-select">
                                <option value="2">2 Guests (Table)</option>
                                <option value="3">3 Guests (Table)</option>
                                <option value="4" selected>4 Guests (Booth)</option>
                                <option value="6">6 Guests (Garden Table)</option>
                                <option value="8">8+ Guests (Chef Table)</option>
                            </select>
                        </div>
                    </div>

                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                        <div class="form-group">
                            <label>Reservation Date</label>
                            <input type="date" id="res-date" class="form-input" required>
                        </div>
                        <div class="form-group">
                            <label>Time Slot</label>
                            <select id="res-time" class="form-select">
                                <option value="10:00 AM">10:00 AM (Brunch)</option>
                                <option value="11:30 AM">11:30 AM (Brunch)</option>
                                <option value="01:00 PM">01:00 PM (Lunch)</option>
                                <option value="06:30 PM" selected>06:30 PM (Dinner)</option>
                                <option value="08:00 PM">08:00 PM (Dinner)</option>
                            </select>
                        </div>
                    </div>

                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                        <div class="form-group">
                            <label>Email Address</label>
                            <input type="email" id="res-email" class="form-input" required placeholder="elena@example.com">
                        </div>
                        <div class="form-group">
                            <label>Seating Preference</label>
                            <select id="res-seating" class="form-select">
                                <option value="Garden Patio">Outdoor Garden Patio</option>
                                <option value="Main Dining Room">Cozy Hearth Dining Room</option>
                                <option value="Bar & Roastery">Barista Roastery Counter</option>
                            </select>
                        </div>
                    </div>

                    <button type="submit" class="btn btn-primary" style="width: 100%; justify-content: center; padding: 12px; margin-top: 8px;">
                        <i class="fa-solid fa-check"></i> Confirm Reservation
                    </button>
                </form>
            </div>
        </div>
    </section>

    <!-- Heritage & About Section -->
    <section class="section-container" id="story" style="border-top: 1px solid var(--border); padding-top: 4rem;">
        <div style="text-align: center; max-width: 680px; margin: 0 auto 3rem;">
            <span class="hero-badge"><i class="fa-solid fa-feather"></i> Our Heritage</span>
            <h2 style="font-family: var(--font-serif); font-size: 32px; margin-bottom: 12px;">Crafted for Those Who Appreciate the Details</h2>
            <p style="color: var(--text-secondary); font-size: 14px; line-height: 1.7;">
                Bella Vista was founded on a simple philosophy: slow food, direct-trade ethical coffee farming, and warm Mediterranean hospitality.
            </p>
        </div>
    </section>

    <!-- Shopping Tray / Order Drawer -->
    <div class="cart-drawer-overlay" id="cart-overlay" onclick="toggleCartDrawer()"></div>
    <div class="cart-drawer" id="cart-drawer">
        <div class="cart-drawer-head">
            <h3><i class="fa-solid fa-bag-shopping" style="color: var(--amber);"></i> Your Order Tray</h3>
            <button class="btn-outline" style="border: none; font-size: 18px; cursor: pointer; color: var(--text-muted);" onclick="toggleCartDrawer()">&times;</button>
        </div>

        <div class="cart-items-list" id="cart-items-container">
            <!-- Dynamically populated -->
        </div>

        <div class="cart-drawer-foot">
            <div class="cart-total-row">
                <span>Subtotal</span>
                <span id="cart-subtotal" style="font-family: var(--font-mono);">$0.00</span>
            </div>
            <div class="cart-total-row">
                <span>Sales Tax (8%)</span>
                <span id="cart-tax" style="font-family: var(--font-mono);">$0.00</span>
            </div>
            <div class="cart-grand-total">
                <span>Total Amount</span>
                <span id="cart-grand-total" style="color: var(--amber); font-family: var(--font-mono);">$0.00</span>
            </div>
            <button class="btn btn-primary" style="width: 100%; justify-content: center; padding: 12px;" onclick="openCheckoutModal()">
                <i class="fa-solid fa-credit-card"></i> Proceed to Order Checkout
            </button>
        </div>
    </div>

    <!-- Checkout Modal -->
    <div class="modal-overlay hidden" id="checkout-modal">
        <div class="modal-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; padding-bottom: 12px; border-bottom: 1px solid var(--border);">
                <h3 style="font-family: var(--font-serif); font-size: 20px;">Complete Your Order</h3>
                <button class="btn-outline" style="border: none; font-size: 18px; cursor: pointer; color: var(--text-muted);" onclick="closeCheckoutModal()">&times;</button>
            </div>

            <form onsubmit="handleOrderSubmit(event)">
                <div class="form-group">
                    <label>Customer Name</label>
                    <input type="text" id="order-customer-name" class="form-input" required placeholder="Elena Vance" value="Elena Vance">
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                    <div class="form-group">
                        <label>Order Type</label>
                        <select id="order-type" class="form-select">
                            <option value="dine_in">Dine-In</option>
                            <option value="takeout">Takeout / Counter Pickup</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Table / Seat</label>
                        <input type="text" id="order-table" class="form-input" placeholder="Table 4" value="Table 4">
                    </div>
                </div>

                <div class="form-group">
                    <label>Special Instructions</label>
                    <input type="text" id="order-notes" class="form-input" placeholder="e.g. Extra hot espresso, oat milk">
                </div>

                <div style="background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 12px; margin-bottom: 1.2rem; font-size: 12.5px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                        <span>Payment Processing:</span>
                        <strong style="color: var(--amber);">Kitchen POS Gateway (:8010)</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span>AutoSRE Protected:</span>
                        <strong style="color: var(--emerald);">ARMED (Zero Downtime)</strong>
                    </div>
                </div>

                <div style="display: flex; gap: 10px;">
                    <button type="button" class="btn btn-outline" style="flex: 1; justify-content: center;" onclick="closeCheckoutModal()">Cancel</button>
                    <button type="submit" id="btn-submit-order" class="btn btn-primary" style="flex: 2; justify-content: center;">
                        <i class="fa-solid fa-check"></i> Place Order Now
                    </button>
                </div>
            </form>
        </div>
    </div>

    <!-- Order Receipt Modal -->
    <div class="modal-overlay hidden" id="receipt-modal">
        <div class="modal-card" style="text-align: center;">
            <div style="width: 56px; height: 56px; border-radius: 50%; background: rgba(16, 185, 129, 0.15); color: var(--emerald); font-size: 26px; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 1rem;">
                <i class="fa-solid fa-circle-check"></i>
            </div>
            <h3 style="font-family: var(--font-serif); font-size: 22px; margin-bottom: 6px;">Order Sent to Kitchen!</h3>
            <p style="color: var(--text-muted); font-size: 13px; margin-bottom: 1.5rem;" id="receipt-order-id">Order #BV-8921</p>
            
            <div style="background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1rem; text-align: left; margin-bottom: 1.5rem; font-size: 13px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="color: var(--text-muted);">Estimated Prep:</span>
                    <strong style="color: var(--amber);">10-12 Minutes</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="color: var(--text-muted);">Table Destination:</span>
                    <strong id="receipt-table">Table 4</strong>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: var(--text-muted);">Total Paid:</span>
                    <strong id="receipt-total" style="font-family: var(--font-mono); color: var(--emerald);">$0.00</strong>
                </div>
            </div>

            <button class="btn btn-primary" style="width: 100%; justify-content: center;" onclick="closeReceiptModal()">
                Back to Cafe Menu
            </button>
        </div>
    </div>

    <!-- =========================================================================
         FLOATING SRE CHAOS DOCK: INJECT RESTAURANT FAILURES & VERIFY IN AUTOSRE
         ========================================================================= -->
    <div class="sre-chaos-dock">
        <!-- Floating Toggle Pill -->
        <button class="sre-dock-toggle" onclick="toggleChaosPanel()">
            <i class="fa-solid fa-flask" style="color: var(--amber);"></i>
            <span>DevOps Chaos Lab</span>
            <span id="chaos-active-badge" class="badge-pill" style="background: var(--emerald); color: #000; font-weight: 800;">HEALTHY</span>
        </button>

        <!-- Chaos Panel -->
        <div class="sre-chaos-panel" id="sre-chaos-panel">
            <div class="sre-panel-head">
                <h4><i class="fa-solid fa-triangle-exclamation" style="color: var(--amber);"></i> Restaurant Failure Simulator</h4>
                <button class="btn-outline" style="border: none; font-size: 16px; cursor: pointer; color: var(--text-muted);" onclick="toggleChaosPanel()">&times;</button>
            </div>

            <p style="font-size: 11.5px; color: var(--text-muted); margin-bottom: 10px;">
                Inject realistic microservice faults into this restaurant app. Watch them get intercepted, analyzed by Gemini, and self-healed in the AutoSRE Console (:8000).
            </p>

            <div class="chaos-btn-grid">
                <button class="chaos-action-btn" id="btn-chaos-db" onclick="injectChaosMode('db_exhaust')">
                    💥 <strong>DB Pool Exhaustion</strong>
                    <div style="font-size: 9.5px; color: var(--text-muted); margin-top: 2px;">503 on Orders & Bookings</div>
                </button>

                <button class="chaos-action-btn" id="btn-chaos-error" onclick="injectChaosMode('error')">
                    ⚠️ <strong>Kitchen Crash (500)</strong>
                    <div style="font-size: 9.5px; color: var(--text-muted); margin-top: 2px;">80% Error Spike</div>
                </button>

                <button class="chaos-action-btn" id="btn-chaos-latency" onclick="injectChaosMode('latency')">
                    ⏳ <strong>4,500ms Latency</strong>
                    <div style="font-size: 9.5px; color: var(--text-muted); margin-top: 2px;">Gateway Timeout Choke</div>
                </button>

                <button class="chaos-action-btn" id="btn-chaos-cpu" onclick="injectChaosMode('cpu_spike')">
                    ⚡ <strong>POS Thread Starvation</strong>
                    <div style="font-size: 9.5px; color: var(--text-muted); margin-top: 2px;">CPU & Mem Saturation</div>
                </button>
            </div>

            <!-- Single-click Alert to AutoSRE -->
            <button class="btn btn-danger" style="width: 100%; justify-content: center; font-size: 11.5px; padding: 8px; margin-bottom: 6px;" onclick="triggerFailureAndNotifyAutoSRE()">
                <i class="fa-solid fa-bolt"></i> Inject Outage & Trigger AutoSRE War Room
            </button>

            <!-- Reset / Self-Heal -->
            <div style="display: flex; gap: 6px;">
                <button class="btn btn-success" style="flex: 1; justify-content: center; font-size: 11.5px; padding: 7px;" onclick="resetChaosMode()">
                    <i class="fa-solid fa-shield-heart"></i> Reset / Self-Heal
                </button>
                <a href="http://127.0.0.1:8000" target="_blank" class="btn btn-outline" style="flex: 1; justify-content: center; font-size: 11.5px; padding: 7px; color: var(--amber);">
                    <i class="fa-solid fa-arrow-up-right-from-square"></i> Open AutoSRE
                </a>
            </div>

            <!-- Live Telemetry Stream Box -->
            <div class="sre-log-console" id="sre-log-stream">
                [POS Gateway Ready] Monitoring /api/v1/orders and reservations...
            </div>
        </div>
    </div>

    <!-- Toast Notification -->
    <div class="toast-msg hidden" id="toast-message">
        <i class="fa-solid fa-circle-check" style="color: var(--amber);"></i>
        <span id="toast-text">Notification message</span>
    </div>

    <!-- Client-side Logic -->
    <script>
        let menuItems = [];
        let cart = {}; // sku -> quantity
        let currentCategory = 'ALL';

        const logConsole = document.getElementById('sre-log-stream');
        function sreLog(msg) {
            const time = new Date().toLocaleTimeString();
            logConsole.innerHTML = `[${time}] ${msg}<br>` + logConsole.innerHTML;
        }

        function showToast(text, isError = false) {
            const toast = document.getElementById('toast-message');
            const toastText = document.getElementById('toast-text');
            toastText.innerText = text;
            if (isError) {
                toast.classList.add('error');
            } else {
                toast.classList.remove('error');
            }
            toast.classList.remove('hidden');
            setTimeout(() => toast.classList.add('hidden'), 4000);
        }

        // Fetch Menu from API
        async function fetchMenu() {
            try {
                const res = await fetch('/api/v1/inventory');
                if (!res.ok) {
                    const err = await res.json();
                    sreLog(`⚠️ GET /api/v1/inventory failed (HTTP ${res.status}): ${err.error || err.detail}`);
                    updateServiceHealthUI(false);
                    return;
                }
                menuItems = await res.json();
                updateServiceHealthUI(true);
                renderMenu();
                sreLog(`✅ Retrieved ${menuItems.length} menu items from Kitchen POS`);
            } catch (e) {
                sreLog(`❌ Network error reaching /api/v1/inventory: ${e.message}`);
                updateServiceHealthUI(false);
            }
        }

        function filterCategory(cat) {
            currentCategory = cat;
            document.querySelectorAll('.category-tab-btn').forEach(btn => {
                btn.classList.remove('active');
                if (btn.innerText.includes(cat) || (cat === 'ALL' && btn.innerText.includes('All'))) {
                    btn.classList.add('active');
                }
            });
            renderMenu();
        }

        function renderMenu() {
            const grid = document.getElementById('menu-items-grid');
            const filtered = currentCategory === 'ALL' 
                ? menuItems 
                : menuItems.filter(item => item.category === currentCategory);

            grid.innerHTML = filtered.map(item => `
                <div class="menu-card">
                    <div>
                        <div class="menu-card-top">
                            <div class="menu-item-icon"><i class="fa-solid ${item.icon || 'fa-utensils'}"></i></div>
                            <span class="badge-pill">${item.badge || item.category}</span>
                        </div>
                        <h4>${item.name}</h4>
                        <p class="desc">${item.description || 'Artisan handcrafted dish made fresh to order.'}</p>
                    </div>
                    <div class="menu-card-footer">
                        <div>
                            <div class="price-tag">$${item.price.toFixed(2)}</div>
                            <span style="font-size: 11px; color: var(--emerald);">${item.prep_time || '10 mins'}</span>
                        </div>
                        <button class="btn-add-tray" onclick="addToCart('${item.sku}')">
                            <i class="fa-solid fa-plus"></i> Add to Tray
                        </button>
                    </div>
                </div>
            `).join('');

            const liveStockCount = document.getElementById('live-stock-count');
            if (liveStockCount) liveStockCount.innerText = `${menuItems.length} items`;
        }

        // Cart Management
        function addToCart(sku) {
            cart[sku] = (cart[sku] || 0) + 1;
            updateCartUI();
            const item = menuItems.find(i => i.sku === sku);
            showToast(`Added ${item ? item.name : 'item'} to order tray!`);
            sreLog(`Tray item added: ${sku} (Qty: ${cart[sku]})`);
        }

        function changeCartQty(sku, delta) {
            if (!cart[sku]) return;
            cart[sku] += delta;
            if (cart[sku] <= 0) delete cart[sku];
            updateCartUI();
        }

        function updateCartUI() {
            const totalCount = Object.values(cart).reduce((a, b) => a + b, 0);
            document.getElementById('cart-item-count').innerText = totalCount;

            const container = document.getElementById('cart-items-container');
            if (totalCount === 0) {
                container.innerHTML = `
                    <div style="padding: 3rem 1rem; text-align: center; color: var(--text-muted); font-size: 13px;">
                        <i class="fa-solid fa-basket-shopping" style="font-size: 32px; color: var(--surface-hover); margin-bottom: 10px; display: block;"></i>
                        Your tray is currently empty.<br>Browse the menu to add artisanal coffee & dining dishes.
                    </div>
                `;
                document.getElementById('cart-subtotal').innerText = '$0.00';
                document.getElementById('cart-tax').innerText = '$0.00';
                document.getElementById('cart-grand-total').innerText = '$0.00';
                return;
            }

            let subtotal = 0;
            container.innerHTML = Object.entries(cart).map(([sku, qty]) => {
                const item = menuItems.find(i => i.sku === sku) || { name: sku, price: 10.0 };
                const lineTotal = item.price * qty;
                subtotal += lineTotal;
                return `
                    <div class="cart-item-row">
                        <div class="cart-item-info">
                            <h5>${item.name}</h5>
                            <span>$${item.price.toFixed(2)} ea</span>
                        </div>
                        <div class="cart-qty-ctrl">
                            <button class="qty-btn" onclick="changeCartQty('${sku}', -1)">-</button>
                            <span style="font-family: var(--font-mono); font-size: 12px; width: 18px; text-align: center;">${qty}</span>
                            <button class="qty-btn" onclick="changeCartQty('${sku}', 1)">+</button>
                        </div>
                    </div>
                `;
            }).join('');

            const tax = subtotal * 0.08;
            const grandTotal = subtotal + tax;

            document.getElementById('cart-subtotal').innerText = `$${subtotal.toFixed(2)}`;
            document.getElementById('cart-tax').innerText = `$${tax.toFixed(2)}`;
            document.getElementById('cart-grand-total').innerText = `$${grandTotal.toFixed(2)}`;
        }

        function toggleCartDrawer() {
            document.getElementById('cart-drawer').classList.toggle('open');
            document.getElementById('cart-overlay').classList.toggle('open');
        }

        function openCheckoutModal() {
            if (Object.keys(cart).length === 0) {
                showToast("Please add items to your tray before placing an order.", true);
                return;
            }
            toggleCartDrawer();
            document.getElementById('checkout-modal').classList.remove('hidden');
        }

        function closeCheckoutModal() {
            document.getElementById('checkout-modal').classList.add('hidden');
        }

        function closeReceiptModal() {
            document.getElementById('receipt-modal').classList.add('hidden');
        }

        // Order Placement Handler (Calls Real Microservice Endpoint)
        async function handleOrderSubmit(event) {
            event.preventDefault();
            const customerName = document.getElementById('order-customer-name').value;
            const orderType = document.getElementById('order-type').value;
            const tableNumber = document.getElementById('order-table').value;
            const notes = document.getElementById('order-notes').value;

            const itemsPayload = Object.entries(cart).map(([sku, qty]) => ({ sku: sku, quantity: qty }));

            sreLog(`⏳ Submitting POST /api/v1/orders/create for ${customerName} (${tableNumber})...`);
            
            const btnSubmit = document.getElementById('btn-submit-order');
            btnSubmit.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Dispatching to Kitchen...';
            btnSubmit.disabled = true;

            try {
                const res = await fetch('/api/v1/orders/create', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        customer_name: customerName,
                        order_type: orderType,
                        table_number: tableNumber,
                        items: itemsPayload,
                        special_notes: notes
                    })
                });

                const data = await res.json();

                if (!res.ok) {
                    // Outage triggered!
                    sreLog(`💥 ORDER FAILED! HTTP ${res.status}: ${data.error || data.detail || 'Service Outage'}`);
                    showToast(`⚠️ Order Failed (HTTP ${res.status}): ${data.error || 'Kitchen Dispatch Error'}`, true);
                    updateServiceHealthUI(false);
                    closeCheckoutModal();

                    // Automatically notify AutoSRE Control Plane
                    await reportFailureToAutoSRE("KitchenOrderProcessingFailure", data.error || "DB pool exhaustion or POS server crash");
                    return;
                }

                // Success
                sreLog(`✅ Order #${data.order_id} created successfully! Total: $${data.total_amount.toFixed(2)}`);
                showToast(`Order #${data.order_id} placed successfully!`);
                closeCheckoutModal();

                document.getElementById('receipt-order-id').innerText = `Order #${data.order_id}`;
                document.getElementById('receipt-table').innerText = tableNumber || 'Counter Pickup';
                document.getElementById('receipt-total').innerText = `$${data.total_amount.toFixed(2)}`;
                document.getElementById('receipt-modal').classList.remove('hidden');

                // Clear cart
                cart = {};
                updateCartUI();
                fetchMenu();
            } catch (e) {
                sreLog(`❌ Network error dispatching order: ${e.message}`);
                showToast(`Network Error: ${e.message}`, true);
                updateServiceHealthUI(false);
            } finally {
                btnSubmit.innerHTML = '<i class="fa-solid fa-check"></i> Place Order Now';
                btnSubmit.disabled = false;
            }
        }

        // Table Reservation Handler
        async function handleReservationSubmit(event) {
            event.preventDefault();
            const name = document.getElementById('res-name').value;
            const guests = parseInt(document.getElementById('res-guests').value, 10);
            const date = document.getElementById('res-date').value;
            const time = document.getElementById('res-time').value;
            const email = document.getElementById('res-email').value;
            const seating = document.getElementById('res-seating').value;

            sreLog(`⏳ Submitting POST /api/v1/reservations for ${name} (${guests} guests on ${date} @ ${time})...`);

            try {
                const res = await fetch('/api/v1/reservations', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        customer_name: name,
                        email: email,
                        phone: "555-0192",
                        guests: guests,
                        reservation_date: date,
                        reservation_time: time,
                        seating_preference: seating
                    })
                });

                const data = await res.json();

                if (!res.ok) {
                    sreLog(`💥 RESERVATION FAILED! HTTP ${res.status}: ${data.error || data.detail}`);
                    showToast(`Reservation Error (HTTP ${res.status}): ${data.error || 'Database Timeout'}`, true);
                    updateServiceHealthUI(false);
                    await reportFailureToAutoSRE("ReservationDatabaseTimeout", data.error || "Database pool exhausted");
                    return;
                }

                sreLog(`✅ Reservation confirmed! ID: ${data.reservation_id}`);
                showToast(`Table confirmed for ${guests} guests on ${date}!`);
                document.getElementById('reservation-form').reset();
            } catch (e) {
                sreLog(`❌ Network error submitting reservation: ${e.message}`);
                showToast(`Network Error: ${e.message}`, true);
            }
        }

        // =========================================================================
        // SRE Chaos Lab Controls
        // =========================================================================
        function toggleChaosPanel() {
            document.getElementById('sre-chaos-panel').classList.toggle('open');
        }

        async function injectChaosMode(mode) {
            let body = {};
            let alertName = "DatabaseConnectionPoolExhausted";
            if (mode === 'db_exhaust') {
                body = { db_exhaust: true };
                alertName = "DatabaseConnectionPoolExhausted";
            }
            if (mode === 'error') {
                body = { error_rate: 0.85 };
                alertName = "KitchenOrderServiceCrash";
            }
            if (mode === 'latency') {
                body = { latency_ms: 4500 };
                alertName = "DownstreamTimeoutCascade";
            }
            if (mode === 'cpu_spike') {
                body = { cpu_spike: true, leak_mb: 50 };
                alertName = "CPUSaturationThreadStarvation";
            }

            sreLog(`💥 Incurring Chaos Mode: ${mode}...`);
            try {
                const res = await fetch('/chaos/inject', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(body)
                });
                const data = await res.json();
                sreLog(`Chaos Active: ${JSON.stringify(data.current_state)}`);
                showToast(`Chaos fault injected: ${mode}! Testing site now in degraded state.`, true);
                checkHealth();
                // Dispatch alert directly to AutoSRE War Room
                reportFailureToAutoSRE(alertName, `Chaos mode ${mode} injected in restaurant-cafe-service`);
            } catch (e) {
                sreLog(`Error injecting chaos: ${e.message}`);
            }
        }

        async function resetChaosMode() {
            sreLog(`🔄 Resetting chaos faults to healthy baseline...`);
            try {
                await fetch('/chaos/reset', { method: 'POST' });
                sreLog(`✅ Chaos cleared. Service restored to 100% operational.`);
                showToast("All chaos faults reset to healthy baseline!");
                checkHealth();
                fetchMenu();
            } catch (e) {
                sreLog(`Error resetting chaos: ${e.message}`);
            }
        }

        // Trigger failure AND alert AutoSRE Control Plane
        async function triggerFailureAndNotifyAutoSRE() {
            sreLog(`💥 Injecting DB Pool Exhaustion + Notifying AutoSRE (:8000)...`);
            await injectChaosMode('db_exhaust');
            await reportFailureToAutoSRE("DatabaseConnectionPoolExhausted", "PostgreSQL pool depleted in restaurant-cafe-service");
        }

        async function reportFailureToAutoSRE(alertName, details) {
            sreLog(`🤖 Dispatching incident alert to AutoSRE Control Plane (http://127.0.0.1:8000/api/incidents/trigger)...`);
            try {
                const res = await fetch('http://127.0.0.1:8000/api/incidents/trigger', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        service_name: 'restaurant-cafe-service',
                        alert_name: alertName,
                        severity: 'CRITICAL'
                    })
                });

                if (res.ok) {
                    const data = await res.json();
                    sreLog(`🤖 AutoSRE Responded! Incident ID: ${data.incident_id}`);
                    sreLog(`🤖 Diagnosis: ${data.result ? data.result.diagnosis : 'Self-healing in progress'}`);
                    sreLog(`🤖 Auto-Remediation Status: ${data.result ? data.result.verification_status : 'INVESTIGATING'}`);
                    showToast(`AutoSRE detected incident ${data.incident_id} & triggered self-healing!`);
                    setTimeout(checkHealth, 1800);
                    setTimeout(fetchMenu, 2200);
                } else {
                    sreLog(`AutoSRE response note: HTTP ${res.status}`);
                }
            } catch (e) {
                sreLog(`AutoSRE bridge note: ${e.message} (Verify AutoSRE is running on :8000)`);
            }
        }

        async function checkHealth() {
            try {
                const res = await fetch('/health');
                const data = await res.json();
                const isHealthy = data.status === 'healthy';
                updateServiceHealthUI(isHealthy, data.db_connected);
            } catch (e) {
                updateServiceHealthUI(false, false);
            }
        }

        function updateServiceHealthUI(isHealthy, dbConnected = true) {
            const badge = document.getElementById('service-health-indicator');
            const chaosBadge = document.getElementById('chaos-active-badge');

            if (isHealthy) {
                badge.style.color = 'var(--emerald)';
                badge.innerHTML = '<i class="fa-solid fa-circle" style="font-size: 8px;"></i> POS ONLINE (:8010)';
                chaosBadge.style.background = 'var(--emerald)';
                chaosBadge.style.color = '#000';
                chaosBadge.innerText = 'HEALTHY';
            } else {
                badge.style.color = 'var(--rose)';
                badge.innerHTML = '<i class="fa-solid fa-triangle-exclamation" style="font-size: 9px;"></i> OUTAGE / DEGRADED';
                chaosBadge.style.background = 'var(--rose)';
                chaosBadge.style.color = '#FFF';
                chaosBadge.innerText = 'OUTAGE ACTIVE';
            }
        }

        // Initialize date picker with today's date
        document.addEventListener('DOMContentLoaded', () => {
            const today = new Date().toISOString().split('T')[0];
            const dateInput = document.getElementById('res-date');
            if (dateInput) dateInput.value = today;
            fetchMenu();
            checkHealth();
            setInterval(checkHealth, 3500);
        });
    </script>
</body>
</html>
"""

# ------------------------------------------------------------------------------
# Core Business Endpoints (Menu, Orders, Table Reservations)
# ------------------------------------------------------------------------------

@app.get("/health")
def health_check():
    """
    Health check endpoint reporting readiness, database pool status,
    and active chaos modes. Supports both restaurant and inventory names.
    """
    is_degraded = (
        chaos_state["db_pool_exhausted"]
        or chaos_state["latency_ms"] > 2000
        or chaos_state["error_rate"] > 0.4
    )
    return {
        "status": "degraded" if is_degraded else "healthy",
        "service": "inventory-service",
        "service_name": "restaurant-cafe-service",
        "display_name": "Bella Vista Artisan Cafe & Bistro",
        "aliases": ["restaurant-cafe-service", "inventory-service"],
        "version": "2.0.0",
        "db_connected": not chaos_state["db_pool_exhausted"],
        "active_chaos": {
            "latency_ms": chaos_state["latency_ms"],
            "error_rate": chaos_state["error_rate"],
            "db_pool_exhausted": chaos_state["db_pool_exhausted"],
            "memory_leak_mb": chaos_state["memory_leak_mb"],
        },
    }

@app.get("/api/v1/inventory")
@app.get("/api/v1/menu")
def list_inventory():
    """Returns the full catalog of cafe menu items and roasts."""
    logger.info("Serving restaurant menu catalog with %d items", len(INVENTORY_DB))
    return list(INVENTORY_DB.values())

@app.get("/api/v1/inventory/{sku}")
def get_item(sku: str):
    if sku not in INVENTORY_DB:
        raise HTTPException(status_code=404, detail=f"Menu item SKU '{sku}' not found in catalog")
    return INVENTORY_DB[sku]

@app.post("/api/v1/inventory/reserve")
def reserve_stock(req: ReserveItemRequest):
    """
    Backward-compatible stock reservation endpoint.
    Maintains compatibility with existing AutoSRE test suite.
    """
    if req.sku not in INVENTORY_DB:
        raise HTTPException(status_code=404, detail=f"Item SKU '{req.sku}' not found")

    item = INVENTORY_DB[req.sku]
    available = item["stock"] - item["reserved"]
    if available < req.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient availability for '{item['name']}'. Requested: {req.quantity}, Available: {available}"
        )

    item["reserved"] += req.quantity
    logger.info("Reserved %d units of %s for order %s. Remaining: %d", req.quantity, req.sku, req.order_id, item["stock"] - item["reserved"])
    return {
        "status": "RESERVED",
        "order_id": req.order_id,
        "sku": req.sku,
        "quantity_reserved": req.quantity,
        "remaining_stock": item["stock"] - item["reserved"],
    }

@app.post("/api/v1/orders/create")
def create_customer_order(order: OrderCreateRequest):
    """
    Consumer ordering endpoint for dine-in and takeaway orders.
    Calculates prices, reserves stock, creates order record.
    """
    if not order.items:
        raise HTTPException(status_code=400, detail="Cannot place empty order")

    order_id = f"BV-{random.randint(1000, 9999)}"
    subtotal = 0.0
    confirmed_items = []

    for item_req in order.items:
        sku = item_req.get("sku")
        qty = item_req.get("quantity", 1)
        if sku not in INVENTORY_DB:
            continue
        
        db_item = INVENTORY_DB[sku]
        if db_item["stock"] - db_item["reserved"] < qty:
            raise HTTPException(
                status_code=400,
                detail=f"Sold out: '{db_item['name']}' only has {db_item['stock'] - db_item['reserved']} available"
            )
        
        db_item["reserved"] += qty
        item_cost = db_item["price"] * qty
        subtotal += item_cost
        confirmed_items.append({
            "sku": sku,
            "name": db_item["name"],
            "quantity": qty,
            "unit_price": db_item["price"],
            "line_total": item_cost
        })

    tax = subtotal * 0.08
    total = subtotal + tax

    order_record = {
        "order_id": order_id,
        "customer_name": order.customer_name,
        "order_type": order.order_type,
        "table_number": order.table_number,
        "items": confirmed_items,
        "subtotal": round(subtotal, 2),
        "tax": round(tax, 2),
        "total_amount": round(total, 2),
        "status": "PREPARING",
        "timestamp": time.time(),
    }
    ORDERS_STORE.append(order_record)
    logger.info("Created customer order %s for %s. Total: $%.2f", order_id, order.customer_name, total)
    return order_record

@app.post("/api/v1/reservations")
def create_table_reservation(res_req: ReservationRequest):
    """
    Consumer table reservation booking endpoint.
    If database connection pool is exhausted, this route fails with HTTP 503.
    """
    reservation_id = f"RES-{random.randint(10000, 99999)}"
    record = {
        "reservation_id": reservation_id,
        "customer_name": res_req.customer_name,
        "email": res_req.email,
        "phone": res_req.phone,
        "guests": res_req.guests,
        "reservation_date": res_req.reservation_date,
        "reservation_time": res_req.reservation_time,
        "seating_preference": res_req.seating_preference,
        "status": "CONFIRMED",
        "created_at": time.time(),
    }
    RESERVATIONS_STORE.append(record)
    logger.info("Confirmed table reservation %s for %s (%d guests on %s @ %s)",
                reservation_id, res_req.customer_name, res_req.guests, res_req.reservation_date, res_req.reservation_time)
    return record

# ------------------------------------------------------------------------------
# Chaos Fault Injection Endpoints
# ------------------------------------------------------------------------------

@app.post("/chaos/inject")
def inject_chaos(config: ChaosConfig):
    chaos_state["latency_ms"] = config.latency_ms or 0
    chaos_state["error_rate"] = config.error_rate or 0.0
    chaos_state["db_pool_exhausted"] = bool(config.db_exhaust)
    chaos_state["cpu_spike"] = bool(config.cpu_spike)

    if config.leak_mb and config.leak_mb > 0:
        chunk = bytearray(config.leak_mb * 1024 * 1024)
        chaos_state["leak_buffer"].append(chunk)
        chaos_state["memory_leak_mb"] += config.leak_mb
        logger.warning("Allocated %d MB leak chunk. Total: %d MB", config.leak_mb, chaos_state["memory_leak_mb"])

    logger.warning(
        "Chaos configured: latency=%dms, error_rate=%.2f, db_exhaust=%s, cpu_spike=%s",
        chaos_state["latency_ms"], chaos_state["error_rate"], chaos_state["db_pool_exhausted"], chaos_state["cpu_spike"]
    )
    return {"status": "chaos_injected", "current_state": chaos_state}

@app.post("/chaos/reset")
def reset_chaos():
    chaos_state["latency_ms"] = 0
    chaos_state["error_rate"] = 0.0
    chaos_state["db_pool_exhausted"] = False
    chaos_state["cpu_spike"] = False
    chaos_state["memory_leak_mb"] = 0
    chaos_state["leak_buffer"].clear()
    logger.info("Restaurant cafe service chaos state reset to healthy baseline.")
    return {"status": "chaos_cleared"}

@app.get("/chaos/status")
def get_chaos_status():
    return chaos_state

# ------------------------------------------------------------------------------
# AutoSRE Remediation Callbacks (Target of AutoSRE Tool Actions)
# ------------------------------------------------------------------------------

@app.post("/remediate/restart")
def handle_remediation_restart():
    """
    Simulates Kubernetes rolling pod restart or state flush.
    Target of AutoSRE SREClusterTools.restart_deployment!
    """
    logger.info("AutoSRE Autonomous Remediation Action Received: Rolling restart & pool flush initiated.")
    # Flush deadlocks and reset failure state
    chaos_state["latency_ms"] = 0
    chaos_state["error_rate"] = 0.0
    chaos_state["db_pool_exhausted"] = False
    chaos_state["cpu_spike"] = False
    chaos_state["leak_buffer"].clear()
    chaos_state["memory_leak_mb"] = 0
    return {
        "action": "restart_deployment",
        "service": "restaurant-cafe-service",
        "status": "RESTARTED",
        "message": "Connection pools flushed, memory buffers reclaimed, restaurant service restored to healthy operation.",
    }

@app.post("/remediate/scale")
def handle_remediation_scale(replicas: int = 3):
    """Simulates Kubernetes HPA horizontal pod scaling."""
    logger.info("AutoSRE Remediation Action Received: Scaling restaurant POS to %d replicas.", replicas)
    return {
        "action": "scale_deployment",
        "service": "restaurant-cafe-service",
        "replicas": replicas,
        "status": "SCALED",
        "message": f"Restaurant cafe service successfully scaled to {replicas} replicas to absorb traffic burst.",
    }

@app.post("/api/trigger-incident-to-autosre")
async def trigger_incident_to_autosre(alert_name: str = "DatabaseConnectionPoolExhausted"):
    """
    Direct bridge to alert AutoSRE Control Plane on port 8000.
    """
    autosre_url = os.getenv("AUTOSRE_URL", "http://127.0.0.1:8000/api/incidents/trigger")
    payload = {
        "service_name": "restaurant-cafe-service",
        "alert_name": alert_name,
        "severity": "CRITICAL"
    }
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.post(autosre_url, json=payload)
            return resp.json()
    except Exception as e:
        logger.warning("Could not reach AutoSRE on %s: %s", autosre_url, e)
        return {"status": "LOCAL_RECORD_ONLY", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8010))
    uvicorn.run(app, host="0.0.0.0", port=port)
