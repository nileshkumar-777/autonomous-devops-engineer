import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Theme Colors
    BG_COLOR = RGBColor(11, 17, 32)         # #0B1120 Deep Midnight Navy
    CARD_BG = RGBColor(30, 41, 59)          # #1E293B Slate Card
    CARD_BG_ALT = RGBColor(15, 23, 42)      # #0F172A Darker Slate
    CARD_BORDER = RGBColor(51, 65, 85)      # #334155 Subtle Slate Border
    BORDER_BLUE = RGBColor(59, 130, 246)    # #3B82F6 Blue Accent Border
    BORDER_GREEN = RGBColor(16, 185, 129)   # #10B981 Green Accent
    BORDER_PURPLE = RGBColor(139, 92, 246)  # #8B5CF6 Purple Accent
    BORDER_AMBER = RGBColor(245, 158, 11)   # #F59E0B Amber Accent
    
    TEXT_TITLE = RGBColor(248, 250, 252)    # #F8FAFC Pure Slate White
    TEXT_BODY = RGBColor(226, 232, 240)     # #E2E8F0 Light Slate Body
    TEXT_MUTED = RGBColor(148, 163, 184)    # #94A3B8 Muted Slate
    
    COLOR_BLUE = RGBColor(59, 130, 246)     # #3B82F6 Indigo Blue
    COLOR_CYAN = RGBColor(56, 189, 248)     # #38BDF8 Cyan
    COLOR_GREEN = RGBColor(52, 211, 153)    # #34D399 Emerald Green
    COLOR_PURPLE = RGBColor(167, 139, 250)  # #A78BFA Violet
    COLOR_AMBER = RGBColor(251, 191, 36)    # #FBBF24 Amber
    COLOR_RED = RGBColor(248, 113, 113)     # #F87171 Red

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.fill.background()
        return bg

    def add_header(slide, badge, title, subtitle):
        # Badge
        badge_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.4), Inches(4.5), Inches(0.35))
        badge_box.fill.solid()
        badge_box.fill.fore_color.rgb = RGBColor(30, 58, 138)  # Deep Indigo
        badge_box.line.color.rgb = COLOR_BLUE
        badge_box.line.width = Pt(1)
        tf_b = badge_box.text_frame
        tf_b.word_wrap = True
        p_b = tf_b.paragraphs[0]
        p_b.text = badge.upper()
        p_b.font.name = "Segoe UI"
        p_b.font.size = Pt(9)
        p_b.font.bold = True
        p_b.font.color.rgb = COLOR_CYAN
        p_b.alignment = PP_ALIGN.CENTER

        # Title
        tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(11.7), Inches(0.6))
        tf_t = tb_title.text_frame
        tf_t.word_wrap = True
        tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
        p_t = tf_t.paragraphs[0]
        p_t.text = title
        p_t.font.name = "Segoe UI"
        p_t.font.size = Pt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_TITLE

        # Subtitle
        tb_sub = slide.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.7), Inches(0.4))
        tf_s = tb_sub.text_frame
        tf_s.word_wrap = True
        tf_s.margin_left = tf_s.margin_top = tf_s.margin_right = tf_s.margin_bottom = 0
        p_s = tf_s.paragraphs[0]
        p_s.text = subtitle
        p_s.font.name = "Segoe UI"
        p_s.font.size = Pt(12)
        p_s.font.color.rgb = TEXT_MUTED

    def add_card(slide, left, top, width, height, bg=CARD_BG, border=CARD_BORDER, border_width=1):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg
        card.line.color.rgb = border
        card.line.width = Pt(border_width)
        return card

    def add_speaker_notes(slide, notes):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = notes

    screenshot_dir = r"C:\Users\ASUS\.gemini\antigravity-ide\brain\76671e28-4906-40ca-91bb-e9ee85c2a03b"

    # =========================================================================
    # SLIDE 1: TITLE SLIDE (ACADEMIC DEFENSE)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    # Big Decorative Glow Box
    glow = add_card(s1, Inches(0.8), Inches(0.8), Inches(11.733), Inches(5.9), bg=RGBColor(15, 23, 42), border=BORDER_BLUE, border_width=1.5)

    # Top Tag
    tag_box = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(1.2), Inches(5.2), Inches(0.38))
    tag_box.fill.solid()
    tag_box.fill.fore_color.rgb = RGBColor(30, 58, 138)
    tag_box.line.color.rgb = COLOR_CYAN
    tag_box.line.width = Pt(1)
    tf = tag_box.text_frame
    p = tf.paragraphs[0]
    p.text = "ACADEMIC DEFENSE • SOFTWARE ARCHITECTURE & DESIGN (SAD)"
    p.font.name = "Segoe UI"
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN
    p.alignment = PP_ALIGN.CENTER

    # Main Project Title
    tb = s1.shapes.add_textbox(Inches(1.2), Inches(1.75), Inches(11.0), Inches(1.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "AUTOSRE: AUTONOMOUS SRE CONTROL PLANE"
    p.font.name = "Segoe UI"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = TEXT_TITLE
    
    p2 = tf.add_paragraph()
    p2.text = "Software Architecture, Multi-Tier Decomposition & Closed-Loop Autonomous Healing for Cloud Systems"
    p2.font.name = "Segoe UI"
    p2.font.size = Pt(15)
    p2.font.color.rgb = COLOR_CYAN
    p2.space_before = Pt(8)

    # Subtitle details
    tb_desc = s1.shapes.add_textbox(Inches(1.2), Inches(3.2), Inches(10.8), Inches(0.9))
    tf_d = tb_desc.text_frame
    tf_d.word_wrap = True
    p_d = tf_d.paragraphs[0]
    p_d.text = "An end-to-end autonomous DevOps & SRE control plane featuring 5-tier layered separation of concerns, 8-node LangGraph finite state machine, Drain+Isolation Forest unsupervised ML, grounded SRE runbook RAG, and deterministic Zero-Shell security boundaries."
    p_d.font.name = "Segoe UI"
    p_d.font.size = Pt(11.5)
    p_d.font.color.rgb = TEXT_MUTED

    # 3 Bottom Feature Cards
    c1 = add_card(s1, Inches(1.2), Inches(4.3), Inches(3.4), Inches(2.0), bg=CARD_BG, border=BORDER_BLUE)
    tf1 = c1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "LAYERED ARCHITECTURE"
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_CYAN
    p2 = tf1.add_paragraph()
    p2.text = "• 5 independent horizontal tiers\n• Presentation, API, AI, Policy, DB\n• Strict separation of concerns (SoC)\n• Blast radius isolation across fleet"
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_BODY
    p2.space_before = Pt(6)

    c2 = add_card(s1, Inches(4.9), Inches(4.3), Inches(3.4), Inches(2.0), bg=CARD_BG, border=BORDER_PURPLE)
    tf2 = c2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "8-NODE LANGGRAPH FSM"
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_PURPLE
    p2 = tf2.add_paragraph()
    p2.text = "• Autonomous Sense-Plan-Act reflex\n• Google Gemini 3.5 Flash Lite RCA\n• Deterministic heuristic fallback\n• Human-in-the-loop approval gate"
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_BODY
    p2.space_before = Pt(6)

    c3 = add_card(s1, Inches(8.6), Inches(4.3), Inches(3.4), Inches(2.0), bg=CARD_BG, border=BORDER_GREEN)
    tf3 = c3.text_frame
    tf3.word_wrap = True
    p = tf3.paragraphs[0]
    p.text = "VERIFIED IN CODEBASE"
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_GREEN
    p2 = tf3.add_paragraph()
    p2.text = "• 36/36 Unit Tests Passing (100%)\n• MTTR reduced: 60+ min -> <15 sec\n• Zero-Shell execution security\n• SQLite 3 WAL immutable audit log"
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_BODY
    p2.space_before = Pt(6)

    add_speaker_notes(s1, (
        "Welcome professors and evaluators. Today I am presenting AutoSRE, an Autonomous DevOps and Site Reliability Engineering Control Plane. "
        "This project is evaluated specifically through the lens of Software Architecture and Design (SAD). "
        "We address one of the most critical challenges in cloud computing: how to transition from high-stress, error-prone manual 3 AM outage triage "
        "to a mathematically bounded, autonomous self-healing system using rigorous 5-tier layered architecture, finite state machines, and safe AI reasoning."
    ))

    # =========================================================================
    # SLIDE 2: THE OPERATIONAL PROBLEM & MOTIVATION
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "1. Motivation & Problem Statement", "The Crisis of Manual SRE at 3 AM vs. Autonomous Self-Healing", "Why traditional DevOps operations fail under modern cloud scale and complexity")

    # Left: Traditional Crisis Card
    card_left = add_card(s2, Inches(0.8), Inches(1.9), Inches(5.7), Inches(3.4), bg=CARD_BG, border=COLOR_RED)
    tf_l = card_left.text_frame
    tf_l.word_wrap = True
    p = tf_l.paragraphs[0]
    p.text = "🔴 THE TRADITIONAL CRISIS (MANUAL SRE)"
    p.font.bold = True
    p.font.size = Pt(12)
    p.font.color.rgb = COLOR_RED
    
    bullets_l = [
        ("Outage at 3 AM: ", "Database connection pool exhausts or memory leak crashes microservice."),
        ("PagerDuty Alerts: ", "On-call engineer woken up groggy; spends 15 mins getting online."),
        ("Manual Log Digging: ", "Grep through gigabytes of raw logs across multiple servers."),
        ("Outdated Runbooks: ", "Engineering wikis are incomplete or missing critical steps."),
        ("Dangerous SSH Commands: ", "Tired engineer types shell commands directly on production."),
        ("High MTTR: ", "Mean Time to Resolve exceeds 45 to 60+ minutes of costly downtime.")
    ]
    for b_title, b_desc in bullets_l:
        p = tf_l.add_paragraph()
        run1 = p.add_run()
        run1.text = "• " + b_title
        run1.font.bold = True
        run1.font.size = Pt(9.5)
        run1.font.color.rgb = TEXT_TITLE
        run2 = p.add_run()
        run2.text = b_desc
        run2.font.size = Pt(9.5)
        run2.font.color.rgb = TEXT_BODY
        p.space_before = Pt(3)

    # Right: AutoSRE Solution Card
    card_right = add_card(s2, Inches(6.8), Inches(1.9), Inches(5.7), Inches(3.4), bg=CARD_BG, border=BORDER_GREEN)
    tf_r = card_right.text_frame
    tf_r.word_wrap = True
    p = tf_r.paragraphs[0]
    p.text = "🟢 THE AUTOSRE SOLUTION (AUTONOMOUS REFLEX)"
    p.font.bold = True
    p.font.size = Pt(12)
    p.font.color.rgb = COLOR_GREEN

    bullets_r = [
        ("Sub-Second Detection: ", "Drain regex parser + Isolation Forest scores anomaly in <8ms."),
        ("Grounded Runbook RAG: ", "TF-IDF vector matcher retrieves official verified SRE runbook."),
        ("Cognitive Root Cause RCA: ", "Google Gemini 3.5 Flash Lite outputs structured JSON diagnosis."),
        ("Zero-Shell Policy Gate: ", "Enforces strict allowlist; high-risk targets pause for human review."),
        ("Automated Remediation: ", "Executes safe Docker restart or pod scale via API (no bash)."),
        ("Ultra-Low MTTR: ", "Complete closed-loop detection, fix, and verification in <15 SECONDS.")
    ]
    for b_title, b_desc in bullets_r:
        p = tf_r.add_paragraph()
        run1 = p.add_run()
        run1.text = "• " + b_title
        run1.font.bold = True
        run1.font.size = Pt(9.5)
        run1.font.color.rgb = TEXT_TITLE
        run2 = p.add_run()
        run2.text = b_desc
        run2.font.size = Pt(9.5)
        run2.font.color.rgb = TEXT_BODY
        p.space_before = Pt(3)

    # Bottom Analogy Box (ICU Monitor)
    card_bot = add_card(s2, Inches(0.8), Inches(5.5), Inches(11.7), Inches(1.5), bg=RGBColor(24, 34, 53), border=COLOR_CYAN)
    tf_b = card_bot.text_frame
    tf_b.word_wrap = True
    p = tf_b.paragraphs[0]
    p.text = "💡 RELATABLE REAL-WORLD ANALOGY: THE INTELLIGENT ICU HOSPITAL MONITOR"
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_CYAN

    p2 = tf_b.add_paragraph()
    p2.text = "Imagine an intensive care unit (ICU) hospital patient. If their heart rhythm crashes at 3 AM, waiting 45 minutes for a nurse to wake up a doctor to look up pharmacology books could be fatal. AutoSRE acts as an intelligent ICU life-support monitor: it continuously senses vitals (metrics), diagnoses the arrhythmia (Gemini RCA), verifies dosage safety rules (Zero-Shell Policy Gate), and delivers the corrective medication in 10 seconds!"
    p2.font.size = Pt(10)
    p2.font.color.rgb = TEXT_BODY
    p2.space_before = Pt(4)

    add_speaker_notes(s2, (
        "In this slide, we contrast traditional manual SRE against AutoSRE. "
        "In production cloud systems, microservices fail unpredictably. Human engineers take an average of 45-60 minutes to resolve incidents "
        "because they must wake up, read raw logs, and find documentation. "
        "AutoSRE automates this entire loop in under 15 seconds. "
        "The ICU hospital monitor analogy makes this intuitive: you cannot afford 45 minutes of downtime when patient vitals or financial transactions are on the line."
    ))

    # =========================================================================
    # SLIDE 3: WHY DO WE NEED SOFTWARE ARCHITECTURE? (SAD CORE)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "2. Foundations of Software Architecture", "Why Do We Need Architecture? The Layered Architecture Primer", "Contrasting the Spaghetti Monolith anti-pattern against rigorous Separation of Concerns (SoC)")

    # Left Card: The Anti-Pattern
    c_anti = add_card(s3, Inches(0.8), Inches(1.9), Inches(5.7), Inches(3.4), bg=CARD_BG, border=COLOR_AMBER)
    tf_a = c_anti.text_frame
    tf_a.word_wrap = True
    p = tf_a.paragraphs[0]
    p.text = "⚠️ THE ANTI-PATTERN: SPAGHETTI MONOLITH ('BIG BALL OF MUD')"
    p.font.bold = True
    p.font.size = Pt(11.5)
    p.font.color.rgb = COLOR_AMBER

    points_anti = [
        ("No Architectural Boundaries: ", "UI buttons directly trigger database queries and execute raw shell scripts."),
        ("Tight Coupling: ", "A minor bug in a frontend CSS or button handler can crash the database or wipe disk files."),
        ("Zero Testability: ", "Impossible to write isolated unit tests; every test requires the entire monolith to be running."),
        ("Uncontained Blast Radius: ", "Failure in a non-critical component (notifications) brings down core payments."),
        ("Unconstrained AI Risk: ", "LLMs given raw shell access will eventually hallucinate destructive commands (rm -rf /).")
    ]
    for b_title, b_desc in points_anti:
        p = tf_a.add_paragraph()
        run1 = p.add_run()
        run1.text = "• " + b_title
        run1.font.bold = True
        run1.font.size = Pt(9.5)
        run1.font.color.rgb = TEXT_TITLE
        run2 = p.add_run()
        run2.text = b_desc
        run2.font.size = Pt(9.5)
        run2.font.color.rgb = TEXT_BODY
        p.space_before = Pt(3)

    # Right Card: The Solution
    c_sol = add_card(s3, Inches(6.8), Inches(1.9), Inches(5.7), Inches(3.4), bg=CARD_BG, border=BORDER_BLUE)
    tf_s = c_sol.text_frame
    tf_s.word_wrap = True
    p = tf_s.paragraphs[0]
    p.text = "🛡️ THE ARCHITECTURAL SOLUTION: LAYERED ARCHITECTURE"
    p.font.bold = True
    p.font.size = Pt(11.5)
    p.font.color.rgb = COLOR_CYAN

    points_sol = [
        ("Separation of Concerns (SoC): ", "System is partitioned into distinct horizontal layers with single responsibilities."),
        ("Strict Inter-Tier Boundaries: ", "Each layer only communicates with adjacent layers; UI never talks directly to DB."),
        ("Independent Evolvability: ", "Replace SQLite with PostgreSQL or switch Gemini to Claude without touching UI."),
        ("Blast Radius Containment: ", "If payment service leaks DB connections, the rest of the fleet stays operational."),
        ("Security Policy Interception: ", "AI outputs are treated as untrusted proposals; gatekeeper checks allowlists before execution.")
    ]
    for b_title, b_desc in points_sol:
        p = tf_s.add_paragraph()
        run1 = p.add_run()
        run1.text = "• " + b_title
        run1.font.bold = True
        run1.font.size = Pt(9.5)
        run1.font.color.rgb = TEXT_TITLE
        run2 = p.add_run()
        run2.text = b_desc
        run2.font.size = Pt(9.5)
        run2.font.color.rgb = TEXT_BODY
        p.space_before = Pt(3)

    # Bottom Card: Restaurant Analogy
    c_rest = add_card(s3, Inches(0.8), Inches(5.5), Inches(11.7), Inches(1.5), bg=RGBColor(24, 34, 53), border=COLOR_PURPLE)
    tf_r = c_rest.text_frame
    tf_r.word_wrap = True
    p = tf_r.paragraphs[0]
    p.text = "🍽️ THE RESTAURANT KITCHEN ANALOGY (EASY ARCHITECTURAL MAPPING)"
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_PURPLE

    p2 = tf_r.add_paragraph()
    p2.text = "• Customer (Presentation Tier): Sits at dining table; orders food. Never enters the kitchen or touches ingredients.\n• Waiter (API Gateway): Carries structured order ticket to kitchen; returns plated food to customer.\n• Chef (Cognitive AI Brain): Plans recipe and cooks the meal based on expert manuals (Runbook RAG).\n• Food Safety Inspector (Policy Gatekeeper): Checks that food adheres to health laws before leaving kitchen.\n• Pantry Refrigerator (Persistence Tier): Stores raw ingredients safely. If refrigerator brand changes, customers never know!"
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_BODY
    p2.space_before = Pt(3)

    add_speaker_notes(s3, (
        "Here we address the core question in Software Architecture & Design: why do we need architecture at all? "
        "Without architecture, software degenerates into the 'Spaghetti Monolith' or 'Big Ball of Mud' anti-pattern. "
        "Layered Architecture enforces Separation of Concerns: each layer has one job. "
        "Our Restaurant Kitchen analogy makes this crystal clear for evaluators: a waiter never cooks, a customer never enters the pantry, "
        "and food is never served without safety inspection. That is exactly how AutoSRE safeguards production systems."
    ))

    # =========================================================================
    # SLIDE 4: THE 5-TIER LAYERED ARCHITECTURE BLUEPRINT
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "3. Multi-Tier Architecture Blueprint", "The 5 Architectural Tiers of AutoSRE", "Strict hierarchical layering from client browser to monitored container infrastructure")

    tiers_data = [
        ("TIER 1: PRESENTATION TIER (OPERATIONAL COCKPIT)", 
         "Executive Glassmorphic UI (HTML5, Vanilla CSS3, ES6 JavaScript, SVG Dynamic Topology Mesh)\n• Live node health indicators, real-time alert war room, dynamic endpoint discovery modal\n• Zero framework build overhead; sub-millisecond reactive DOM updates via Server-Sent Events",
         COLOR_CYAN, Inches(1.85)),
        ("TIER 2: API GATEWAY & ORCHESTRATION TIER", 
         "FastAPI ASGI Asynchronous Application Server (Python 3.12)\n• 17 validated REST API contracts with Pydantic v2 schemas; OpenAPI autogenerated documentation\n• CORS security headers, async non-blocking request routing, webhook ingestors for GitHub and Vercel",
         COLOR_BLUE, Inches(2.95)),
        ("TIER 3: OBSERVABILITY & COGNITIVE REASONING TIER", 
         "Prometheus Metric Scraper (:9090) + Drain Regex Parser + Isolation Forest Anomaly Detection (<8ms)\n• 8-Node LangGraph State Machine orchestrating incident reflex arc; TF-IDF SRE Runbook RAG retriever\n• Google Gemini 3.5 Flash Lite cognitive reasoner generating structured JSON root-cause diagnosis",
         COLOR_PURPLE, Inches(4.05)),
        ("TIER 4: SECURITY POLICY & EXECUTION TIER", 
         "Deterministic Zero-Shell Policy Gatekeeper (Action Allowlist: restart, scale, rollback, clear_cache)\n• Human-in-the-Loop authorization gate for high-blast-radius targets (`payment-service` / `production`)\n• Safe container tool execution via Docker SDK & Kubernetes APIs; automated HTTP /health verification loop",
         COLOR_AMBER, Inches(5.15)),
        ("TIER 5: PERSISTENCE & INFRASTRUCTURE TIER", 
         "SQLite 3 with Write-Ahead Logging (WAL Mode) + SQLAlchemy 2.0 ORM Engine\n• Immutable Audit Ledger (`audit_ledger`), Incident History (`incidents`), Target Connectors (`system_connectors`)\n• Monitored Fleet: user-service (:8001), payment (:8002), order (:8003), notif (:8004), Bella Vista Cafe (:8010)",
         COLOR_GREEN, Inches(6.25))
    ]

    for title, desc, col, y_pos in tiers_data:
        c = add_card(s4, Inches(0.8), y_pos, Inches(11.7), Inches(0.95), bg=CARD_BG, border=col)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.08)
        tf.margin_left = Inches(0.15)
        p = tf.paragraphs[0]
        p.text = title
        p.font.bold = True
        p.font.size = Pt(10.5)
        p.font.color.rgb = col

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(8.5)
        p2.font.color.rgb = TEXT_BODY
        p2.space_before = Pt(2)

    add_speaker_notes(s4, (
        "This slide presents the formal 5-tier layered architecture blueprint of AutoSRE. "
        "Notice the clean progression from Tier 1 (Presentation) down to Tier 5 (Persistence and Infrastructure). "
        "Every layer has an explicit responsibility. For example, Tier 3 (Cognitive Reasoning) formulates a remediation proposal, "
        "but Tier 3 has ZERO execution authority. Only Tier 4 (Policy & Execution) can invoke Docker SDK calls, and only after verifying allowlists. "
        "This architectural constraint mathematically prevents runaway AI agents."
    ))

    # =========================================================================
    # SLIDE 5: APPLIED ARCHITECTURAL STYLES & DESIGN PATTERNS
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "4. Architectural Styles & Design Patterns", "Design Patterns Applied Across the AutoSRE Ecosystem", "How proven software engineering patterns guarantee predictability, safety, and performance")

    patterns = [
        ("Layered / Multi-Tier", "5-tier separation (UI, API, AI, Policy, DB)", "Separation of Concerns: Allows independent upgrades of UI, database, or ML models without cascade breaks.", COLOR_CYAN),
        ("Microservices", "Fleet: user, payment, order, notif, cafe", "Blast Radius Containment: A connection pool leak in payment-service cannot take down user authentication.", COLOR_BLUE),
        ("Finite State Machine", "LangGraph 8-Node Agent (src/agent/graph.py)", "Predictability: Agent moves strictly through audited states; guarantees no infinite AI loops or stalls.", COLOR_PURPLE),
        ("Observer Pattern", "Prometheus Telemetry Scraper (:9090)", "Loose Coupling: Control plane observes microservice health without modifying target source code.", COLOR_GREEN),
        ("Facade / API Gateway", "FastAPI Control Plane (src/backend/app.py)", "Unified Interface: Clients and dashboards interact with one unified API rather than juggling 10 services.", COLOR_CYAN),
        ("Gatekeeper / Interceptor", "Zero-Shell Policy Gate (src/agent/policies.py)", "Security Barrier: Intercepts all AI outputs before execution; validates against strict action allowlist.", COLOR_AMBER),
        ("Strategy Pattern", "Dual-Mode Reasoner (Gemini vs. Fallback)", "High Availability: Uses Gemini 3.5 Lite when online; instantly switches to heuristic rules if API quota limits hit.", COLOR_PURPLE),
        ("RAG Pattern", "Runbook Retriever (src/rag/retriever.py)", "Grounded Truth: Feeds verified Markdown SRE manuals into Gemini context, eliminating hallucinations.", COLOR_GREEN)
    ]

    card_w = Inches(2.78)
    card_h = Inches(2.35)
    xs = [Inches(0.8), Inches(3.78), Inches(6.75), Inches(9.72)]
    ys = [Inches(2.0), Inches(4.65)]

    for idx, (p_name, p_impl, p_why, p_col) in enumerate(patterns):
        col_idx = idx % 4
        row_idx = idx // 4
        x = xs[col_idx]
        y = ys[row_idx]

        c = add_card(s5, x, y, card_w, card_h, bg=CARD_BG, border=p_col)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.12)
        tf.margin_top = Inches(0.1)

        p = tf.paragraphs[0]
        p.text = p_name.upper()
        p.font.bold = True
        p.font.size = Pt(10)
        p.font.color.rgb = p_col

        p2 = tf.add_paragraph()
        run = p2.add_run()
        run.text = "Implemented in: "
        run.font.bold = True
        run.font.size = Pt(8)
        run.font.color.rgb = TEXT_TITLE
        run2 = p2.add_run()
        run2.text = p_impl
        run2.font.size = Pt(8)
        run2.font.color.rgb = COLOR_CYAN
        p2.space_before = Pt(3)

        p3 = tf.add_paragraph()
        run = p3.add_run()
        run.text = "Why Needed: "
        run.font.bold = True
        run.font.size = Pt(8)
        run.font.color.rgb = TEXT_TITLE
        run2 = p3.add_run()
        run2.text = p_why
        run2.font.size = Pt(8)
        run2.font.color.rgb = TEXT_BODY
        p3.space_before = Pt(3)

    add_speaker_notes(s5, (
        "Software Architecture is defined by the patterns it embodies. "
        "Here we show the 8 core patterns implemented in AutoSRE. "
        "For example, the Gatekeeper pattern protects production from AI hallucinations; the Strategy pattern allows our reasoner "
        "to toggle between Gemini 3.5 Lite and offline heuristic rules for 100% availability; and the Observer pattern allows Prometheus "
        "to monitor microservices without injecting intrusive agent sidecars into user code."
    ))

    # =========================================================================
    # SLIDE 6: COMPONENT & CONNECTOR (C&C) ARCHITECTURE & DATA FLOW
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "5. Component & Connector (C&C) Architecture", "Runtime Data Flow & Inter-Component Communication", "End-to-end data pipeline from telemetry scrape to verified remediation")

    # Step-by-step pipeline cards
    steps = [
        ("1. TELEMETRY SCRAPE", "Prometheus Scraper & Microservices Fleet", "Microservices emit /metrics & logs. Scraper samples CPU, memory, error rates, and thread counts.", COLOR_CYAN),
        ("2. LOG ANOMALY CHECK", "Drain Regex Parser + Isolation Forest", "Drain abstracts variables (<IP>, <NUM>). Isolation Forest scores template vectors in <8ms.", COLOR_BLUE),
        ("3. SENSING ANOMALY", "LangGraph Agent Triggered", "If anomaly score < -0.15 or 5xx spike occurs, an incident is registered and agent reflex kicks off.", COLOR_PURPLE),
        ("4. RUNBOOK RAG MATCH", "TF-IDF Vector Space Retriever", "Retriever queries SRE Markdown guides (5 runbooks) and extracts matching resolution chunk.", COLOR_GREEN),
        ("5. COGNITIVE AI RCA", "Google Gemini 3.5 Flash Lite", "LLM consumes metrics + anomaly logs + runbook chunk; generates structured JSON root-cause diagnosis.", COLOR_CYAN),
        ("6. POLICY GATEKEEPER", "Zero-Shell Safety Allowlist", "Gatekeeper verifies tool allowlist. If service is protected (payment), shifts to Human Approval.", COLOR_AMBER),
        ("7. SAFE TOOL EXECUTION", "Docker SDK / Kubernetes API", "Tool invoker triggers container restart or replica scaling without any interactive bash shell.", COLOR_GREEN),
        ("8. AUDIT LEDGER COMMIT", "SQLite 3 WAL Database", "Verification probe polls /health across 3 retries (200 OK); commits immutable audit log entry.", COLOR_BLUE)
    ]

    card_w = Inches(2.78)
    card_h = Inches(2.35)
    xs = [Inches(0.8), Inches(3.78), Inches(6.75), Inches(9.72)]
    ys = [Inches(2.0), Inches(4.65)]

    for idx, (s_title, s_comp, s_desc, s_col) in enumerate(steps):
        col_idx = idx % 4
        row_idx = idx // 4
        x = xs[col_idx]
        y = ys[row_idx]

        c = add_card(s6, x, y, card_w, card_h, bg=CARD_BG, border=s_col)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.12)
        tf.margin_top = Inches(0.1)

        p = tf.paragraphs[0]
        p.text = s_title
        p.font.bold = True
        p.font.size = Pt(10)
        p.font.color.rgb = s_col

        p2 = tf.add_paragraph()
        run = p2.add_run()
        run.text = s_comp
        run.font.bold = True
        run.font.size = Pt(8.5)
        run.font.color.rgb = TEXT_TITLE
        p2.space_before = Pt(2)

        p3 = tf.add_paragraph()
        p3.text = s_desc
        p3.font.size = Pt(8)
        p3.font.color.rgb = TEXT_BODY
        p3.space_before = Pt(3)

    add_speaker_notes(s6, (
        "In Software Architecture and Design, Component and Connector (C&C) views describe the runtime flow of data and control. "
        "Here we trace the 8 runtime stages of AutoSRE. Notice that every connector is explicitly defined. "
        "Telemetry moves from the fleet to the ML engine; when an anomaly is detected, LangGraph invokes the RAG retriever, "
        "which feeds context to Gemini 3.5 Lite. The policy gatekeeper intercepts the output, and only after validation is the tool executed "
        "and committed to the audit ledger."
    ))

    # =========================================================================
    # SLIDE 7: BEHAVIORAL ARCHITECTURE: 8-NODE LANGGRAPH FSM
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "6. Behavioral Architecture & State Machine", "The 8-Node LangGraph Autonomous Reflex Arc", "Finite State Machine (FSM) ensuring deterministic, audited, and recoverable transitions")

    # Top Flowchart Bar
    c_flow = add_card(s7, Inches(0.8), Inches(1.9), Inches(11.7), Inches(1.1), bg=CARD_BG_ALT, border=BORDER_PURPLE)
    tf_fl = c_flow.text_frame
    tf_fl.word_wrap = True
    p = tf_fl.paragraphs[0]
    p.text = "FINITE STATE MACHINE TRANSITION PATHWAY:"
    p.font.bold = True
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_PURPLE

    p2 = tf_fl.add_paragraph()
    p2.text = "[MONITORING] ➔ [ANALYZING (ML+RAG+LLM)] ➔ [GATEKEEPING] ➔ [PENDING_APPROVAL / EXECUTING] ➔ [VERIFYING] ➔ [RESOLVED]"
    p2.font.bold = True
    p2.font.size = Pt(11)
    p2.font.color.rgb = COLOR_CYAN
    p2.space_before = Pt(4)

    # 4 Phase Cards Below
    phases = [
        ("1. SENSE PHASE", "Nodes: scrape_telemetry, detect_anomaly", 
         "• Pulls live Prometheus metrics\n• Drain regex masks dynamic tokens\n• Isolation Forest scores anomaly\n• Triggers incident if score < -0.15", COLOR_CYAN),
        ("2. PLAN PHASE", "Nodes: retrieve_runbook, llm_rca_reasoning", 
         "• TF-IDF cosine similarity search\n• Indexes 5 curated SRE runbooks\n• Google Gemini 3.5 Flash Lite RCA\n• Generates structured JSON diagnosis", COLOR_PURPLE),
        ("3. GATEKEEP PHASE", "Nodes: policy_gatekeeper", 
         "• Enforces strict 5-action allowlist\n• Blocks interactive bash/sh shells\n• If target is protected (payment):\n  pauses in PENDING_APPROVAL\n• Human SRE approves in War Room", COLOR_AMBER),
        ("4. ACT & VERIFY PHASE", "Nodes: execute_remediation, verify_health, commit_audit", 
         "• Invokes safe Docker SDK action\n• Polls /health up to 3 retries\n• Verifies latency & HTTP 200 OK\n• Writes immutable audit record\n• Shifts state to RESOLVED", COLOR_GREEN)
    ]

    card_w = Inches(2.78)
    card_h = Inches(3.8)
    xs = [Inches(0.8), Inches(3.78), Inches(6.75), Inches(9.72)]

    for idx, (p_title, p_nodes, p_desc, p_col) in enumerate(phases):
        x = xs[idx]
        c = add_card(s7, x, Inches(3.2), card_w, card_h, bg=CARD_BG, border=p_col)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.12)
        tf.margin_top = Inches(0.12)

        p = tf.paragraphs[0]
        p.text = p_title
        p.font.bold = True
        p.font.size = Pt(11)
        p.font.color.rgb = p_col

        p2 = tf.add_paragraph()
        p2.text = p_nodes
        p2.font.bold = True
        p2.font.size = Pt(8.5)
        p2.font.color.rgb = TEXT_TITLE
        p2.space_before = Pt(3)

        p3 = tf.add_paragraph()
        p3.text = p_desc
        p3.font.size = Pt(9)
        p3.font.color.rgb = TEXT_BODY
        p3.space_before = Pt(6)

    add_speaker_notes(s7, (
        "Behavioral modeling is essential in SAD. Unlike naive LLM scripts that run open-ended bash loops, "
        "AutoSRE uses LangGraph to construct a formal Finite State Machine (FSM). "
        "The agent transitions through 4 clear phases: Sense, Plan, Gatekeep, and Act & Verify. "
        "Crucially, the Gatekeep phase allows the system to enter a pause state (PENDING_APPROVAL) where human operators can intervene."
    ))

    # =========================================================================
    # SLIDE 8: ARCHITECTURAL QUALITY ATTRIBUTES (NFRS) & ADRS
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "7. Quality Attributes & Decision Records", "Non-Functional Requirements (NFRs) & Architectural Decision Records (ADRs)", "Evaluating architectural trade-offs, engineering rationale, and non-functional guarantees")

    # Left: NFRs Card
    c_nfr = add_card(s8, Inches(0.8), Inches(1.9), Inches(5.7), Inches(5.1), bg=CARD_BG, border=COLOR_CYAN)
    tf_n = c_nfr.text_frame
    tf_n.word_wrap = True
    p = tf_n.paragraphs[0]
    p.text = "🎯 ARCHITECTURAL QUALITY ATTRIBUTES (NFRS)"
    p.font.bold = True
    p.font.size = Pt(11.5)
    p.font.color.rgb = COLOR_CYAN

    nfrs = [
        ("Availability (MTTR <15s): ", "System continuously self-heals in seconds. Dual-mode heuristic fallback ensures 100% control plane availability even during external API downtime."),
        ("Security & Safety: ", "Deterministic Zero-Shell boundary blocks all arbitrary command execution. High-blast-radius targets require explicit cryptographic human sign-off."),
        ("Performance & Latency: ", "Drain log parsing and Isolation Forest inference complete in <8ms. SQLite WAL journaling allows lock-free concurrent reads without thread blocking."),
        ("Modularity & Maintainability: ", "Layered boundaries allow independent component upgrades (e.g. swapping Gemini with Claude, or SQLite with PostgreSQL) with zero ripple effects."),
        ("Explainability & Auditability: ", "Every AI diagnosis cites specific runbook chunks and outputs a confidence score (0.0 to 1.0). Every action is permanently written to the audit ledger.")
    ]
    for b_title, b_desc in nfrs:
        p = tf_n.add_paragraph()
        run1 = p.add_run()
        run1.text = "• " + b_title
        run1.font.bold = True
        run1.font.size = Pt(9)
        run1.font.color.rgb = TEXT_TITLE
        run2 = p.add_run()
        run2.text = b_desc
        run2.font.size = Pt(8.5)
        run2.font.color.rgb = TEXT_BODY
        p.space_before = Pt(4)

    # Right: ADRs Card
    c_adr = add_card(s8, Inches(6.8), Inches(1.9), Inches(5.7), Inches(5.1), bg=CARD_BG, border=BORDER_PURPLE)
    tf_ad = c_adr.text_frame
    tf_ad.word_wrap = True
    p = tf_ad.paragraphs[0]
    p.text = "📋 ARCHITECTURAL DECISION RECORDS (ADRS)"
    p.font.bold = True
    p.font.size = Pt(11.5)
    p.font.color.rgb = COLOR_PURPLE

    adrs = [
        ("ADR-01: LangGraph FSM vs. Linear Chains", "Adopted cyclic state machine to support retry verification loops and human pause states; linear chains cannot loop safely."),
        ("ADR-02: Zero-Shell Policy vs. Free Shell Access", "Adopted strict 5-action allowlist; completely eliminates the risk of catastrophic AI hallucinations (e.g. rm -rf /)."),
        ("ADR-03: Isolation Forest vs. LLM Log Parsing", "Adopted unsupervised ML for log scoring; achieves <8ms latency and linear time complexity without expensive cloud API token bills."),
        ("ADR-04: SQLite 3 WAL vs. External PostgreSQL", "Adopted embedded SQLite with WAL journaling for zero external operational dependencies, zero-admin setup, and ACID reliability."),
        ("ADR-05: Hybrid Runbook RAG vs. Fine-Tuning", "Adopted TF-IDF Markdown RAG; allows SRE engineers to update runbooks in real-time as markdown files without slow model retraining.")
    ]
    for b_title, b_desc in adrs:
        p = tf_ad.add_paragraph()
        run1 = p.add_run()
        run1.text = "• " + b_title + "\n  "
        run1.font.bold = True
        run1.font.size = Pt(9)
        run1.font.color.rgb = TEXT_TITLE
        run2 = p.add_run()
        run2.text = b_desc
        run2.font.size = Pt(8.5)
        run2.font.color.rgb = TEXT_BODY
        p.space_before = Pt(3)

    add_speaker_notes(s8, (
        "In academic Software Architecture, Quality Attributes (NFRs) and Architectural Decision Records (ADRs) are essential. "
        "Here we show that every architectural choice had clear alternatives and engineering trade-offs. "
        "For instance, ADR-01 chose LangGraph FSM over simple linear chains because self-healing requires cyclic retry loops. "
        "ADR-02 chose a Zero-Shell policy allowlist over raw bash execution to mathematically guarantee safety."
    ))

    # =========================================================================
    # SLIDE 9: DEVELOPMENT METHODOLOGY: WATERFALL VS. SRE CONTINUOUS LIFECYCLE
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "8. Software Development Methodology", "Why Waterfall Fails for Cloud Operations vs. SRE Continuous Lifecycle", "Contrasting rigid sequential delivery against continuous, automated closed-loop resilience")

    # Table of comparison
    rows, cols = 6, 3
    left, top, width, height = Inches(0.8), Inches(1.9), Inches(11.7), Inches(3.2)
    tbl_shape = s9.shapes.add_table(rows, cols, left, top, width, height)
    tbl = tbl_shape.table
    tbl.columns[0].width = Inches(2.3)
    tbl.columns[1].width = Inches(4.7)
    tbl.columns[2].width = Inches(4.7)

    headers = ["Evaluation Dimension", "Traditional Waterfall Model", "AutoSRE SRE Continuous Agile Lifecycle"]
    for c_idx, h_text in enumerate(headers):
        cell = tbl.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(30, 58, 138)
        p = cell.text_frame.paragraphs[0]
        p.text = h_text
        p.font.bold = True
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_TITLE

    table_data = [
        ("Process Workflow", "Strictly sequential (Phase N+1 cannot start until Phase N is 100% finished & signed off).", "Continuous, cyclic reflex loops: Sense -> Plan -> Act -> Verify."),
        ("Requirements Flexibility", "Rigidly frozen upfront for 6 to 12 months; changes are extremely costly.", "Dynamic & adaptive: auto-discovers newly registered endpoints & adapts to API drift."),
        ("Testing Philosophy", "Late 'Big-Bang' manual testing at the very end of the project lifecycle.", "36 automated unit tests (100% pass) + proactive Chaos Engineering fire drills."),
        ("Outage Recovery", "Human paged at 3 AM; 45+ minutes manual SSH log digging (High MTTR).", "Autonomous reflex arc: Detects, diagnoses, and heals in under 15 seconds."),
        ("System Resilience", "Fragile: unforeseen production bugs cause prolonged system outages.", "Resilient: Heuristic fallback ensures 100% uptime; Zero-Shell safety guardrails.")
    ]

    for r_idx, (d1, d2, d3) in enumerate(table_data):
        row = r_idx + 1
        vals = [d1, d2, d3]
        for c_idx, val in enumerate(vals):
            cell = tbl.cell(row, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = CARD_BG if row % 2 == 1 else CARD_BG_ALT
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(8.5)
            p.font.color.rgb = TEXT_TITLE if c_idx == 0 else TEXT_BODY

    # Bottom Takeaway Card
    c_bot = add_card(s9, Inches(0.8), Inches(5.3), Inches(11.7), Inches(1.7), bg=RGBColor(24, 34, 53), border=COLOR_AMBER)
    tf_b = c_bot.text_frame
    tf_b.word_wrap = True
    p = tf_b.paragraphs[0]
    p.text = "🔥 CORE SAD LESSON: WHY WATERFALL FAILS IN CLOUD OPERATIONS"
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_AMBER

    p2 = tf_b.add_paragraph()
    p2.text = "In cloud microservices, failures (traffic spikes, memory leaks, connection pool exhaustion) are dynamic and unpredictable. You cannot freeze operational requirements for 6 months! If a microservice crashes at 3 AM, you cannot tell the production system to wait for a 6-month Waterfall phase. AutoSRE embraces Chaos Engineering: just like running hospital fire drills, we deliberately inject faults to verify that the system detects, plans, and heals automatically in under 15 seconds."
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_BODY
    p2.space_before = Pt(3)

    add_speaker_notes(s9, (
        "Here we discuss software development methodologies as requested. "
        "The Waterfall model is rigid: requirements are frozen upfront, and testing occurs only at the very end. "
        "In cloud DevOps and SRE, Waterfall fails catastrophically because cloud failures are dynamic and emergent. "
        "AutoSRE adopts the SRE Continuous Agile Lifecycle: we use automated unit testing and Chaos Engineering fire drills "
        "to continuously validate that our autonomous reflex arc handles unforeseen incidents safely."
    ))

    # =========================================================================
    # SLIDE 10: OPERATIONAL COCKPIT: 4-PANEL SCREENSHOT SHOWCASE
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "9. Visual Operational Cockpit", "Verified Live Dashboard Implementation (4-Panel Showcase)", "Sub-millisecond glassmorphic UI displaying real-time telemetry, AI war room, and chaos testing")

    img_w = Inches(5.7)
    img_h = Inches(2.2)
    cards_pos = [
        (Inches(0.8), Inches(1.9), "gemini_rca_war_room_1791068379213.png", "Fig 1: Incident War Room — Gemini 3.5 Lite RCA & Approved Tool Execution", COLOR_CYAN),
        (Inches(6.8), Inches(1.9), "connected_cafe_state_1791067700862.png", "Fig 2: Executive Fleet Mesh Topology — Live Monitored Target Nodes", COLOR_BLUE),
        (Inches(0.8), Inches(4.7), "endpoint_discovery_modal_1791066127753.png", "Fig 3: Endpoint Discovery Modal — Dynamic Target Registration & Toggle", COLOR_PURPLE),
        (Inches(6.8), Inches(4.7), "cafe_devops_chaos_lab_1791062764320.png", "Fig 4: Target Application (Bella Vista Cafe) Built-in Chaos Injection Lab", COLOR_GREEN)
    ]

    for x, y, img_name, caption, border_col in cards_pos:
        img_path = os.path.join(screenshot_dir, img_name)
        # Background card
        add_card(s10, x, y, img_w, Inches(2.6), bg=CARD_BG, border=border_col)
        # Picture
        if os.path.exists(img_path):
            s10.shapes.add_picture(img_path, x + Inches(0.08), y + Inches(0.08), img_w - Inches(0.16), img_h)
        # Caption
        tb_c = s10.shapes.add_textbox(x + Inches(0.1), y + Inches(2.3), img_w - Inches(0.2), Inches(0.25))
        tf_c = tb_c.text_frame
        tf_c.word_wrap = True
        tf_c.margin_left = tf_c.margin_top = 0
        p_c = tf_c.paragraphs[0]
        p_c.text = caption
        p_c.font.name = "Segoe UI"
        p_c.font.size = Pt(8)
        p_c.font.bold = True
        p_c.font.color.rgb = border_col

    add_speaker_notes(s10, (
        "Here we showcase the actual running operational cockpit captured from our live test sessions. "
        "Top-left (Fig 1) shows the Incident War Room with Google Gemini 3.5 Flash Lite root-cause analysis and confidence rating. "
        "Top-right (Fig 2) shows the SVG topology mesh with live node latencies and health states. "
        "Bottom-left (Fig 3) shows the dynamic endpoint discovery modal. "
        "Bottom-right (Fig 4) shows our Chaos Lab, which lets evaluators inject connection pool leaks and CPU spikes in real time."
    ))

    # =========================================================================
    # SLIDE 11: END-TO-END OPERATIONAL CASE STUDY TRACE
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)
    add_header(s11, "10. End-to-End Case Study Trace", "Autonomous Healing of Payment Service DB Pool Exhaustion", "Step-by-step trace of a live chaos incident resolved autonomously in 11.4 seconds")

    steps_trace = [
        ("Step 1: Chaos Injected", "Chaos lab exhausts database connection pool (50/50 active connections) on payment-service."),
        ("Step 2: Anomaly Detected", "Telemetry scraper intercepts 5xx error surge; Drain parser scores template anomaly at -0.28 (<8ms)."),
        ("Step 3: Runbook Retrieved", "TF-IDF retriever matches database_connection_pool_exhausted.md runbook chunk with 0.89 cosine score."),
        ("Step 4: Gemini RCA Reasoned", "Gemini 3.5 Lite diagnoses leaked connections; proposes restart_deployment with 0.95 confidence."),
        ("Step 5: Policy Gatekeeper", "Gatekeeper identifies payment-service as high-blast-radius; safely holds action in PENDING_APPROVAL."),
        ("Step 6: Human Approval", "SRE operator reviews RCA and confidence meter in War Room; clicks 'Approve Action' button."),
        ("Step 7: Safe Tool Executed", "Tool executor issues safe container restart via Docker SDK without opening any bash shell."),
        ("Step 8: Automated Verification", "Health probe polls /health across 3 retries; verifies latency drops to 4ms and returns HTTP 200 OK."),
        ("Step 9: Audit Log Committed", "Incident marked 'resolved'; immutable record written to SQLite audit ledger. Total MTTR: 11.4 SECONDS!")
    ]

    card_w = Inches(3.75)
    card_h = Inches(1.55)
    xs = [Inches(0.8), Inches(4.78), Inches(8.75)]
    ys = [Inches(1.9), Inches(3.6), Inches(5.3)]

    for idx, (st_title, st_desc) in enumerate(steps_trace):
        col_idx = idx % 3
        row_idx = idx // 3
        x = xs[col_idx]
        y = ys[row_idx]

        col = COLOR_CYAN if idx < 3 else (COLOR_PURPLE if idx < 6 else COLOR_GREEN)
        c = add_card(s11, x, y, card_w, card_h, bg=CARD_BG, border=col)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.12)
        tf.margin_top = Inches(0.1)

        p = tf.paragraphs[0]
        p.text = st_title.upper()
        p.font.bold = True
        p.font.size = Pt(9.5)
        p.font.color.rgb = col

        p2 = tf.add_paragraph()
        p2.text = st_desc
        p2.font.size = Pt(8.5)
        p2.font.color.rgb = TEXT_BODY
        p2.space_before = Pt(3)

    add_speaker_notes(s11, (
        "This slide presents our actual end-to-end case study: resolving a payment-service database connection pool exhaustion incident. "
        "In a traditional setup, this incident causes 45+ minutes of downtime. "
        "AutoSRE completes all 9 steps — detection, runbook retrieval, Gemini RCA, human gatekeeping, Docker restart, verification, and audit logging — "
        "in just 11.4 seconds. This is a 99.6% reduction in Mean Time to Resolve."
    ))

    # =========================================================================
    # SLIDE 12: VERIFICATION FRAMEWORK & IMPLEMENTATION SCOPE
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12)
    add_header(s12, "11. Verification & Implementation Scope", "Rigorous Test Suite & Implementation Scope Matrix", "Empirical verification: 36/36 unit tests passing across all control plane layers")

    # Left: Test Suite Table
    c_test = add_card(s12, Inches(0.8), Inches(1.9), Inches(5.7), Inches(5.1), bg=CARD_BG, border=BORDER_GREEN)
    tf_t = c_test.text_frame
    tf_t.word_wrap = True
    p = tf_t.paragraphs[0]
    p.text = "🧪 VERIFICATION FRAMEWORK: 36/36 PASSING TESTS"
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_GREEN

    test_suites = [
        ("test_agent.py (3 tests): ", "LangGraph state transitions, policy allowlist enforcement, cyclic reflex loop control."),
        ("test_backend.py (3 tests): ", "FastAPI REST routes, incident triggers, status aggregation, CORS security headers."),
        ("test_connectors.py (8 tests): ", "External endpoint discovery, synthetic health pings, Vercel & GitHub webhook ingestors."),
        ("test_microservices.py (11 tests): ", "Fleet health probes, Prometheus metrics scraping, CRUD ops, chaos injection endpoints."),
        ("test_ml_anomaly.py (6 tests): ", "Drain regex variable masking, Isolation Forest normal vs anomaly log scoring (<8ms)."),
        ("test_rag.py (5 tests): ", "Markdown runbook semantic index, TF-IDF cosine similarity ranking, irrelevant query handling.")
    ]
    for b_title, b_desc in test_suites:
        p = tf_t.add_paragraph()
        run1 = p.add_run()
        run1.text = "• " + b_title
        run1.font.bold = True
        run1.font.size = Pt(8.5)
        run1.font.color.rgb = TEXT_TITLE
        run2 = p.add_run()
        run2.text = b_desc
        run2.font.size = Pt(8)
        run2.font.color.rgb = TEXT_BODY
        p.space_before = Pt(3)

    p_pass = tf_t.add_paragraph()
    p_pass.text = "OVERALL OUTCOME: 36/36 TESTS PASSING (100% PASS RATE)"
    p_pass.font.bold = True
    p_pass.font.size = Pt(9.5)
    p_pass.font.color.rgb = COLOR_GREEN
    p_pass.space_before = Pt(6)

    # Right: Scope Matrix
    c_scope = add_card(s12, Inches(6.8), Inches(1.9), Inches(5.7), Inches(5.1), bg=CARD_BG, border=BORDER_BLUE)
    tf_sc = c_scope.text_frame
    tf_sc.word_wrap = True
    p = tf_sc.paragraphs[0]
    p.text = "📊 IMPLEMENTATION SCOPE MATRIX"
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_CYAN

    scope_items = [
        ("Dashboard UI: ", "Implemented: Dark glassmorphic cockpit, SVG topology mesh, war room, discovery modal."),
        ("Control Plane: ", "Implemented: FastAPI async routes, Pydantic validation, CORS, connector registry."),
        ("Agent Engine: ", "Implemented: 8-node LangGraph state machine with cyclic verifier loop."),
        ("Cognitive LLM: ", "Implemented: Google Gemini 3.5 Flash Lite + Heuristic offline fallback rules."),
        ("ML Log Engine: ", "Implemented: Drain regex structural parser + Isolation Forest model (<8ms latency)."),
        ("Runbook RAG: ", "Implemented: TF-IDF cosine similarity search over 5 curated markdown runbooks."),
        ("Security Gate: ", "Implemented: Zero-Shell execution boundary, action allowlist, human approval gate."),
        ("Database: ", "Implemented: SQLite 3 with SQLAlchemy 2.0 ORM, WAL concurrent reading."),
        ("Enterprise Scope: ", "Proposed Future: Multi-agent consensus (Auditor), FAISS vector DB, OAuth2/OIDC.")
    ]
    for b_title, b_desc in scope_items:
        p = tf_sc.add_paragraph()
        run1 = p.add_run()
        run1.text = "• " + b_title
        run1.font.bold = True
        run1.font.size = Pt(8.5)
        run1.font.color.rgb = TEXT_TITLE
        run2 = p.add_run()
        run2.text = b_desc
        run2.font.size = Pt(8)
        run2.font.color.rgb = TEXT_BODY
        p.space_before = Pt(2.5)

    add_speaker_notes(s12, (
        "In this slide, we present the empirical verification of our architecture. "
        "We have 36 automated unit tests passing with a 100% pass rate across all 6 subsystems. "
        "Furthermore, our scope matrix clearly delineates what is verified and implemented in code versus what is proposed for future enterprise expansion."
    ))

    # =========================================================================
    # SLIDE 13: ARCHITECTURAL EVALUATION & CONCLUSION (Q&A)
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_background(s13)
    add_header(s13, "12. Architectural Evaluation & Defense Sign-Off", "Summary of SAD Contributions, Key Takeaways & Defense Q&A", "Formal defense sign-off for Software Architecture & Design (SAD) evaluation")

    # 3 Summary Cards
    c1 = add_card(s13, Inches(0.8), Inches(1.9), Inches(3.7), Inches(3.3), bg=CARD_BG, border=COLOR_CYAN)
    tf1 = c1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "1. ARCHITECTURAL RIGOR"
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_CYAN
    p2 = tf1.add_paragraph()
    p2.text = "• 5-tier layered architecture guarantees strict separation of concerns (SoC).\n• Eliminates the Spaghetti Monolith anti-pattern.\n• Monitored microservices are protected by strict blast radius boundaries."
    p2.font.size = Pt(9)
    p2.font.color.rgb = TEXT_BODY
    p2.space_before = Pt(6)

    c2 = add_card(s13, Inches(4.8), Inches(1.9), Inches(3.7), Inches(3.3), bg=CARD_BG, border=BORDER_PURPLE)
    tf2 = c2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "2. COGNITIVE & SAFE"
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_PURPLE
    p2 = tf2.add_paragraph()
    p2.text = "• Combines Google Gemini 3.5 Lite cognitive reasoning with deterministic Zero-Shell policy boundaries.\n• Runbook RAG eliminates hallucinations.\n• Human-in-the-loop ensures critical actions require operator authorization."
    p2.font.size = Pt(9)
    p2.font.color.rgb = TEXT_BODY
    p2.space_before = Pt(6)

    c3 = add_card(s13, Inches(8.8), Inches(1.9), Inches(3.7), Inches(3.3), bg=CARD_BG, border=BORDER_GREEN)
    tf3 = c3.text_frame
    tf3.word_wrap = True
    p = tf3.paragraphs[0]
    p.text = "3. EMPIRICAL RESULTS"
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_GREEN
    p2 = tf3.add_paragraph()
    p2.text = "• Reduces Mean Time to Resolve (MTTR) from 60+ minutes to <15 seconds.\n• 36/36 unit tests verified passing.\n• Immutable SQLite 3 WAL audit ledger ensures complete accountability."
    p2.font.size = Pt(9)
    p2.font.color.rgb = TEXT_BODY
    p2.space_before = Pt(6)

    # Bottom Q&A Box
    c_qa = add_card(s13, Inches(0.8), Inches(5.4), Inches(11.7), Inches(1.6), bg=RGBColor(24, 34, 53), border=BORDER_BLUE)
    tf_q = c_qa.text_frame
    tf_q.word_wrap = True
    p = tf_q.paragraphs[0]
    p.text = "🎓 PROJECT DEFENSE SIGN-OFF & OPEN FOR QUESTIONS (Q&A)"
    p.font.bold = True
    p.font.size = Pt(12)
    p.font.color.rgb = COLOR_CYAN
    p.alignment = PP_ALIGN.CENTER

    p2 = tf_q.add_paragraph()
    p2.text = "AutoSRE proves that autonomous self-healing is not about giving AI open-ended shell access, but about wrapping cognitive models inside disciplined, multi-tier software architecture and finite state machines.\n\nThank you, professors and evaluators! Questions & Technical Discussion Welcome."
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_BODY
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(4)

    add_speaker_notes(s13, (
        "In conclusion, AutoSRE demonstrates that the secret to safe autonomous AI in DevOps is rigorous Software Architecture. "
        "By enforcing layered separation of concerns, finite state machines, and a Zero-Shell policy boundary, "
        "we achieve sub-15-second incident remediation while mathematically protecting production environments. "
        "Thank you for your time, and I am now ready to answer any questions regarding the software architecture and design."
    ))

    # Save presentation
    output_path = os.path.join(r"c:\autonomous devops engineer", "AutoSRE_Software_Architecture_Presentation.pptx")
    prs.save(output_path)
    print(f"[SUCCESS] Presentation successfully created at: {output_path}")

if __name__ == "__main__":
    create_presentation()
