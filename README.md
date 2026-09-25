# 🤖 Autonomous DevOps Engineer (AutoSRE)

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Kind-326CE5.svg)](https://kubernetes.io/)
[![LangGraph](https://img.shields.io/badge/AI_Agent-LangGraph-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An intelligent, autonomous **Site Reliability Engineering (SRE) & DevOps platform** designed to monitor cloud microservices, detect anomalies, analyze root causes using machine learning and LLMs, formulate remediation plans under safety guardrails, and execute closed-loop self-healing on Kubernetes.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph Microservices ["Target Infrastructure (Kubernetes/Docker)"]
        US["User Service (:8001)"]
        PS["Payment Service (:8002)"]
        OS["Order Service (:8003)"]
        NS["Notification Service (:8004)"]
    end

    subgraph Observability ["Telemetry & Metrics Scrapers"]
        PR["Prometheus (:9090)"]
        GF["Grafana (:3000)"]
        US & PS & OS & NS -->|"Expose /metrics"| PR
        PR --> GF
    end

    subgraph ControlPlane ["FastAPI SRE Control Plane (:8000)"]
        GW["Incident Gateway"]
        AL["Audit & Safety Ledger"]
        DB[(PostgreSQL)]
        RC[(Redis Cache)]
    end

    subgraph AI_Brains ["Diagnostic & Intelligence Brains"]
        ML["ML Anomaly Detector<br/>(Isolation Forest on BGL/HDFS)"]
        RAG["RAG Runbook DB<br/>(FAISS Vector Store)"]
        LLM["LLM Diagnostic Reasoner<br/>(Root Cause Analysis)"]
    end

    subgraph AgentLoop ["LangGraph Autonomous Self-Healing Engine"]
        ES["1. Incident Ingestion"] --> TS["2. Telemetry Scraper"]
        TS --> RG["3. Runbook Query"]
        RG --> DR["4. LLM Diagnosis"]
        DR --> PG{"5. Policy Gatekeeper<br/>(Allowlist & Guardrails)"}
        PG -->|"Approved"| EX["6. Tool Executor<br/>(K8s API Actions)"]
        PG -->|"Blocked / High Risk"| HA["Require Human Approval"]
        EX --> VL{"7. Verification Loop<br/>(Metrics Re-check)"}
        VL -->|"Healthy"| CL["Incident Resolved"]
        VL -->|"Degraded"| DR
    end

    PR -->|"Alert Webhook"| GW
    GW --> ES
    TS --> ML
    RG --> RAG
    DR --> LLM
    EX -->|"Restart / Scale / Rollback"| Microservices
```

---

## 📁 Repository Structure

```text
autonomous-devops-engineer/
├── README.md                           # Master architectural overview & docs
├── requirements.txt                    # Python workspace dependencies
├── docker-compose.yml                  # Local orchestration for all 4 microservices
├── .gitignore                          # Excludes huge datasets, logs, virtualenv, and secrets
│
├── docs/                               # Architecture blueprints & roadmaps
│   ├── complete_implementation_checklist.md # 10-Phase master implementation checklist
│   └── roadmap-portal/                 # Interactive visual learning & architecture reference
│       ├── index.html
│       ├── style.css
│       └── app_v6.js
│
├── datasets/                           # Benchmark system logs (BGL, HDFS, AWSCTD - gitignored)
│
├── src/                                # Source Code
│   ├── microservices/                  # Production target microservices
│   │   ├── user-service/               # User profiles & auth API (:8001)
│   │   ├── payment-service/            # Payment gateway with DB pool simulation (:8002)
│   │   ├── order-service/              # Order pipeline calling payments (:8003)
│   │   └── notification-service/       # Event dispatcher & alerts (:8004)
│   ├── ml/                             # Phase 4: Machine Learning Log Anomaly Engine
│   │   ├── log_parser.py               # BGL / HDFS log preprocessor
│   │   ├── feature_extractor.py        # TF-IDF & sliding window feature extraction
│   │   ├── train_model.py              # Isolation Forest training script
│   │   └── inference_api.py            # Real-time anomaly detection REST API
│   ├── backend/                        # Phase 5: FastAPI OOP SRE Control Plane
│   ├── rag/                            # Phase 6: Vector Knowledge Base & Runbooks
│   │   ├── runbooks/                   # SRE operational runbooks (Markdown)
│   │   └── retriever.py                # FAISS vector similarity search engine
│   ├── agent/                          # Phase 8-9: LangGraph Agent & Closed-Loop Controller
│   │   ├── graph.py                    # Multi-node LangGraph state machine
│   │   ├── tools.py                    # Kubernetes SDK tools (restart, scale, rollback)
│   │   ├── policies.py                 # Allowlist security & permission gatekeeper
│   │   └── verifier.py                 # Post-action telemetry verification
│   └── dashboard/                      # Phase 10: Production React/Web SRE Dashboard
│
├── kubernetes/                         # Kubernetes Deployment Manifests
│   └── manifests/                      # Namespaces, Deployments, Services, ConfigMaps
│
└── tests/                              # Automated Test Suite
    ├── unit/                           # Service and model unit tests
    └── integration/                    # Multi-service cascading failure tests
```

---

## ⚡ Quick Start (Local Development)

### 1. Set Up Python Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Run All Microservices with Docker Compose
```powershell
docker compose up --build
```
The services will be reachable at:
- **User Service:** [http://localhost:8001/docs](http://localhost:8001/docs)
- **Payment Service:** [http://localhost:8002/docs](http://localhost:8002/docs)
- **Order Service:** [http://localhost:8003/docs](http://localhost:8003/docs)
- **Notification Service:** [http://localhost:8004/docs](http://localhost:8004/docs)

### 3. Run Automated Tests
```powershell
pytest -v tests/
```

---

## 🛡️ SRE Safety & Guardrails
- **No Arbitrary Shell Execution**: The AI agent cannot execute bash, PowerShell, or `os.system` calls.
- **Strict Tool Allowlist**: Only explicit, validated methods (`restart_pod`, `scale_replicas`, `rollback_deployment`) can be invoked.
- **Human-in-the-Loop**: Destructive actions or low-confidence diagnoses require human operator approval.
- **Closed-Loop Verification**: The agent monitors Prometheus telemetry for 30–60 seconds after every remediation action to verify resolution.
