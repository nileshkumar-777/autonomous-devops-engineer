# Complete Step-by-Step Implementation Checklist

This document is your actual step-by-step implementation guide for building the **Autonomous DevOps Engineer** project. It is structured chronologically by dependency. Complete every step in sequence. Do not proceed to a new phase until all checkpoints in the current phase have passed.

---

## Phase 0 — Project Planning

Before writing code or configuring clusters, we must establish the system architecture, service schemas, and security boundaries.

### [ ] Task 0.1: Define Complete System Architecture
* **Why:** Maps out how the developer UI, FastAPI backend, LangGraph agent, ML brains, and Kubernetes environment interact, preventing integration conflicts later.
* **Tools/Technologies:** Mermaid.js, diagrams, or visual mapping tools.
* **Implementation:** Create a text-based architecture model mapping the data flow:
  1. Developer queries React Dashboard.
  2. Dashboard calls FastAPI gateway.
  3. FastAPI invokes LangGraph state agent.
  4. Agent queries Prometheus (metrics), logs container outputs, and runs semantic search on RAG (vector database) + ML anomaly score.
  5. LLM diagnoses the incident and suggests a safe action.
  6. Action passes Policy allowlist validator.
  7. Executor uses Kubernetes Client API to restart/scale pods.
* **Expected Result:** Clear architectural design diagram linking all 5 layers (UI, Backend, Agent, ML/RAG, Kubernetes infra).
* **Checkpoint:** visual confirmation that all input/output contracts between layers are defined.

### [ ] Task 0.2: Define Services and Responsibilities
* **Why:** Establishes the target microservices we will deploy, troubleshoot, and monitor.
* **Tools/Technologies:** REST API, Python FastAPI.
* **Implementation:** Document the 4 microservices to be built:
  - `user-service`: Manages customer login and profile storage.
  - `order-service`: Manages ordering pipeline and checks payment status.
  - `payment-service`: Simulates stripe/bank charges. Highly sensitive, target for latency/failure tests.
  - `notification-service`: Dispatches emails or webhook alerts.
* **Expected Result:** A detailed service layout document listing endpoints, dependencies, and database schemas.
* **Checkpoint:** Every service has its HTTP routes (e.g. `/orders`, `/pay`, `/users`) defined on paper.

### [ ] Task 0.3: Define Repository and Directory Structure
* **Why:** Organizes folders to keep backend code, frontend dashboard, model training scripts, and K8s YAML files separated.
* **Tools/Technologies:** Standard directory tree layout.
* **Implementation:** Establish this workspace folder layout structure:
  ```text
  /Autonomous Devops Engineer
    /src
      /microservices
        /user-service
        /order-service
        /payment-service
        /notification-service
      /backend            <-- FastAPI OOP SRE control plane
      /dashboard          <-- React frontend tracking portal
      /ml                 <-- Isolation Forest training & pipelines
      /rag                <-- FAISS indexers and runbooks
    /kubernetes           <-- Deployments, configmaps, and secrets
    /tests                <-- Unit, integration, and recovery tests
  ```
* **Expected Result:** Clean folder skeleton documenting where future scripts reside.
* **Checkpoint:** Directory layout is saved to documentation references.

### [ ] Task 0.4: Define Technology Choices
* **Why:** Clarifies details of the tech stack to avoid switching dependencies mid-development.
* **Tools/Technologies:** Language standards.
* **Implementation:** Finalize stack configurations:
  - Language: Python 3.10+ (Backend, ML, RAG, K8s SDK).
  - API Framework: FastAPI (Uvicorn server).
  - AI Engine: LangGraph + LangChain + OpenAI API / local Llama.
  - Vector DB: FAISS or Chroma.
  - Database: PostgreSQL (SQLAlchemy ORM).
  - Cache: Redis.
  - Observability: Prometheus + Grafana.
  - Containerization: Docker + Kubernetes (Kind / Minikube).
* **Expected Result:** Version list documenting chosen technology modules.
* **Checkpoint:** confirmed access to API keys (e.g. OpenAI) or local LLM runtimes (e.g. Ollama).

### [ ] Task 0.5: Define Data Flows
* **Why:** Clarifies path metrics, alerts, logs, and commands take during troubleshooting loops.
* **Tools/Technologies:** Logging streams, Prometheus scrapes.
* **Implementation:** Map data flows for two states:
  - Normal operation: K8s pods -> metrics scraped by Prometheus -> metrics aggregated on Grafana.
  - Anomaly state: Outage occurs -> Alertmanager fires webhook -> FastAPI creates Incident -> LangGraph agent analyzes -> Executor fixes -> Verifier checks Metrics.
* **Expected Result:** Data flow sequence diagram.
* **Checkpoint:** Validated that Prometheus alerts webhook destination points to FastAPI incident API.

### [ ] Task 0.6: Define Security Boundaries
* **Why:** Restricts AI agent capabilities to prevent accidental deletion of namespaces or arbitrary command injection.
* **Tools/Technologies:** Policy rules, allowlists.
* **Implementation:** Draft the core security rules:
  1. The LLM cannot run shell commands (`subprocess.run` or `os.system` are blocked).
  2. All agent commands must be structured (e.g. `restart_pod(pod_name)`) and validated against an allowlist.
  3. Risky actions (e.g. `rollback_deployment`, `scale_replicas`) require manual human click approval on the dashboard.
* **Expected Result:** A security policy document detailing allowlisted actions.
* **Checkpoint:** Allowlist limits are defined (only restarts, rollbacks, and scales allowed).

---

## Phase 1 — Development Environment

Set up your physical operating system workspace, install core command-line tools, and check software versions.

### [ ] Task 1.1: Install Required DevOps Tools
* **Why:** Prepares command line binaries required to build containers and configure clusters.
* **Tools/Technologies:** Docker Desktop, Helm, Chocolatey (Windows package manager).
* **Implementation:** Open PowerShell as Administrator and execute:
  ```powershell
  # Install Helm for K8s package management
  choco install kubernetes-helm -y
  # Install Git
  choco install git -y
  ```
  Ensure Docker Desktop is downloaded from the official website and running.
* **Expected Result:** Binaries installed and added to your user Path environment variables.
* **Checkpoint:** Running `helm version` and `docker --version` in terminal prints active version numbers.

### [ ] Task 1.2: Configure Python Workspace
* **Why:** Sets up virtual environments to prevent library conflicts between ML and FastAPI libraries.
* **Tools/Technologies:** Python 3.10+, Virtualenv.
* **Implementation:** Create and trigger a local environment in your workspace root:
  ```powershell
  # Verify Python installation
  python --version
  # Create virtual environment named '.venv'
  python -m venv .venv
  # Activate virtual environment
  .venv\Scripts\Activate.ps1
  # Update pip package manager
  python -m pip install --upgrade pip
  ```
* **Expected Result:** Virtualenv folder `.venv` is created in workspace, and shell prompt displays `(.venv)`.
* **Checkpoint:** Running `Get-Command pip` points to your local `.venv\Scripts\pip.exe`.

### [ ] Task 1.3: Configure Docker Environment
* **Why:** Enables building container images locally and running services isolated from host environments.
* **Tools/Technologies:** WSL2, Docker daemon.
* **Implementation:** Open Docker Settings -> general -> Ensure WSL2-based engine is enabled.
* **Expected Result:** Docker daemon runs in the background.
* **Checkpoint:** Running `docker run hello-world` successfully pulls, runs, and outputs hello message.

### [ ] Task 1.4: Configure Kubernetes Locally
* **Why:** Creates a local multi-node Kubernetes container lab on your computer.
* **Tools/Technologies:** Kind (Kubernetes in Docker).
* **Implementation:** Install Kind and spin up a cluster config:
  ```powershell
  # Download Kind binary via chocolatey
  choco install kind -y
  # Create cluster configuration mapping port 80 and 443
  kind create cluster --name devops-lab
  ```
* **Expected Result:** A Kubernetes cluster starts running inside Docker containers.
* **Checkpoint:** Running `docker ps` displays a container named `devops-lab-control-plane`.

### [ ] Task 1.5: Configure kubectl CLI
* **Why:** Controls cluster states, deploys pods, and inspects errors.
* **Tools/Technologies:** kubectl.
* **Implementation:** Install kubectl and check config context mapping:
  ```powershell
  # Install kubectl
  choco install kubernetes-cli -y
  # Point kubectl context to Kind cluster
  kubectl cluster-info --context kind-devops-lab
  ```
* **Expected Result:** Output displays cluster endpoints (Kubernetes control plane URL).
* **Checkpoint:** Running `kubectl get namespaces` displays namespaces: `default`, `kube-system`, `kube-public`.

### [ ] Task 1.6: Create Git Repository and Branch Layout
* **Why:** Enables version control and stores tracking states.
* **Tools/Technologies:** Git.
* **Implementation:** Initialize Git, write a `.gitignore`, and create branches:
  ```powershell
  git init
  # Create gitignore ignoring virtualenv and cache configs
  echo ".venv/" >> .gitignore
  echo "__pycache__/" >> .gitignore
  echo "*.pkl" >> .gitignore
  git add .
  git commit -m "Initial commit"
  # Create dev branch
  git checkout -b development
  ```
* **Expected Result:** Repository initialized, tracked, and set to `development` branch.
* **Checkpoint:** Running `git status` shows zero untracked files except `.gitignore` files.

### [ ] Task 1.7: Create Directory Layout
* **Why:** Builds physical folders mapping out our project.
* **Tools/Technologies:** Windows Shell.
* **Implementation:** Run creation commands in root workspace directory:
  ```powershell
  mkdir -p src/microservices/user-service/app
  mkdir -p src/microservices/order-service/app
  mkdir -p src/microservices/payment-service/app
  mkdir -p src/microservices/notification-service/app
  mkdir -p src/backend/app
  mkdir -p src/dashboard
  mkdir -p src/ml
  mkdir -p src/rag/data
  mkdir -p kubernetes/manifests
  mkdir -p tests
  ```
* **Expected Result:** Folders created on disk.
* **Checkpoint:** File explorer shows all directories present under workspace path.

---

## Phase 2 — Sample Microservices

Develop the FastAPI application stubs representing our target production cluster environment.

### [ ] Task 2.1: Implement User Service
* **Why:** Represents a baseline service managing user records.
* **Tools/Technologies:** Python, FastAPI, Uvicorn.
* **Implementation:** Create `src/microservices/user-service/app/main.py`:
  ```python
  from fastapi import FastAPI
  import logging
  logging.basicConfig(level=logging.INFO)
  logger = logging.getLogger("user-service")

  app = FastAPI(title="User Service")

  @app.get("/")
  def read_root():
      logger.info("Handling root index request")
      return {"service": "user-service", "status": "online"}

  @app.get("/users/{user_id}")
  def get_user(user_id: int):
      logger.info(f"Retrieving user details for id: {user_id}")
      return {"user_id": user_id, "name": f"User_{user_id}", "email": f"user{user_id}@lab.com"}

  @app.get("/health")
  def health():
      return {"status": "healthy"}
  ```
* **Expected Result:** API script written.
* **Checkpoint:** running `uvicorn app.main:app --port 8001 --reload` (inside directory) lets you load http://localhost:8001/health returning HTTP 200.

### [ ] Task 2.2: Implement Order Service
* **Why:** Service managing orders; relies on payment-service to process money transactions.
* **Tools/Technologies:** FastAPI, HTTP client requests.
* **Implementation:** Create `src/microservices/order-service/app/main.py` exposing `/orders` API routes.
* **Expected Result:** Order service logic files written.
* **Checkpoint:** Running the script on port 8002 returns healthy json status payload.

### [ ] Task 2.3: Implement Payment Service
* **Why:** Processes monetary items. This will be our target service to simulate high latency or DB connection pool exhaustion.
* **Tools/Technologies:** FastAPI, time simulation.
* **Implementation:** Create `src/microservices/payment-service/app/main.py`. Include a latency simulation route parameter:
  ```python
  import time
  # Simulates processing with a sleep parameter
  @app.post("/pay")
  def process_payment(amount: float, delay: float = 0):
      if delay > 0:
          time.sleep(delay)
      return {"status": "paid", "amount": amount}
  ```
* **Expected Result:** Payment API script written.
* **Checkpoint:** Accessing `/pay?amount=99&delay=2` takes exactly 2 seconds to respond.

### [ ] Task 2.4: Implement Notification Service
* **Why:** Dispatches warnings, emails, or logs alert incidents.
* **Tools/Technologies:** FastAPI.
* **Implementation:** Write notification app at `src/microservices/notification-service/app/main.py` exposing `/notify` route.
* **Expected Result:** Notification endpoints created.
* **Checkpoint:** Triggering `/notify` returns success message.

### [ ] Task 2.5: Configure Local Database Sandbox
* **Why:** Standardizes storage for microservices before deployment to K8s.
* **Tools/Technologies:** PostgreSQL.
* **Implementation:** Create a temporary PostgreSQL container in Docker to test schemas:
  ```powershell
  docker run --name pg-test -e POSTGRES_PASSWORD=secret -d -p 5432:5432 postgres:15
  ```
* **Expected Result:** Database container running.
* **Checkpoint:** Pinging port 5432 using a database client establishes a connection.

---

## Phase 3 — Docker Packaging

Package all FastAPI microservices into clean, repeatable Docker container images.

### [ ] Task 3.1: Write Dockerfiles for Microservices
* **Why:** Declares how to build individual container environments for each API service.
* **Tools/Technologies:** Dockerfile, python-slim base image.
* **Implementation:** In `src/microservices/payment-service/Dockerfile` (repeat for all 4 services, adjusting directory names):
  ```dockerfile
  FROM python:3.10-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  COPY ./app ./app
  EXPOSE 8000
  CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
  ```
* **Expected Result:** Dockerfile saved.
* **Checkpoint:** requirements.txt containing `fastapi`, `uvicorn`, and `requests` exists in directory.

### [ ] Task 3.2: Build Microservice Docker Images
* **Why:** Compiles source files and dependencies into runnable Docker images on disk.
* **Tools/Technologies:** Docker build engine.
* **Implementation:** Run builds:
  ```powershell
  docker build -t payment-service:v1.0 ./src/microservices/payment-service
  docker build -t order-service:v1.0 ./src/microservices/order-service
  docker build -t user-service:v1.0 ./src/microservices/user-service
  docker build -t notification-service:v1.0 ./src/microservices/notification-service
  ```
* **Expected Result:** Build scripts execute without errors.
* **Checkpoint:** Running `docker images` lists all 4 service images with tag `v1.0`.

### [ ] Task 3.3: Configure Bridge Network & Inter-container Communication
* **Why:** Allows containers to resolve each other's hostnames when running outside Kubernetes.
* **Tools/Technologies:** Docker Network.
* **Implementation:** Create bridge network and launch payment container inside it:
  ```powershell
  # Create network
  docker network create lab-network
  # Run payment container on network
  docker run -d --name payment --network lab-network -p 8003:8000 payment-service:v1.0
  ```
* **Expected Result:** Container active on bridge network.
* **Checkpoint:** Running `docker network inspect lab-network` lists `payment` under container mappings.

### [ ] Task 3.4: Orchestrate Local Environment with Docker Compose
* **Why:** Starts all microservices and databases with a single command for testing.
* **Tools/Technologies:** Docker Compose.
* **Implementation:** Create `src/microservices/docker-compose.yaml` detailing services, env contexts, and PostgreSQL configurations.
* **Expected Result:** Compose file written.
* **Checkpoint:** Running `docker-compose up -d` launches 4 services + Postgres database successfully.

---

## Phase 4 — Kubernetes Orchestration

Deploy your containerized microservices to the local Kubernetes cluster namespace.

### [ ] Task 4.1: Create Namespace and Configs
* **Why:** Isolates lab workloads from other system components.
* **Tools/Technologies:** kubectl, Kubernetes Namespaces.
* **Implementation:** Write `kubernetes/manifests/namespace.yaml`:
  ```yaml
  apiVersion: v1
  kind: Namespace
  metadata:
    name: production
  ```
  Apply it: `kubectl apply -f kubernetes/manifests/namespace.yaml`
* **Expected Result:** Production namespace active in cluster.
* **Checkpoint:** `kubectl get ns` returns `production` namespace.

### [ ] Task 4.2: Write Database StatefulSet & Service Manifests
* **Why:** Ensures stable hostname resolution and persistent storage volumes for the PostgreSQL pod.
* **Tools/Technologies:** StatefulSet, ClusterIP.
* **Implementation:** Create `kubernetes/manifests/postgres.yaml` mapping data volumes and port 5432. Apply to production namespace.
* **Expected Result:** DB resource configs accepted.
* **Checkpoint:** `kubectl get statefulsets -n production` displays `postgres` with 1 active replica.

### [ ] Task 4.3: Deploy Microservices with Health Probes
* **Why:** deploys the microservices to K8s, configuring automated health checks (liveness/readiness probes) so K8s can restart unhealthy pods.
* **Tools/Technologies:** Kubernetes Deployments, Liveness/Readiness probes.
* **Implementation:** Create `kubernetes/manifests/payment-deployment.yaml`:
  ```yaml
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: payment-service
    namespace: production
    labels:
      app: payment-service
  spec:
    replicas: 2
    selector:
      matchLabels:
        app: payment-service
    template:
      metadata:
        labels:
          app: payment-service
      spec:
        containers:
        - name: payment
          image: payment-service:v1.0
          imagePullPolicy: IfNotPresent
          ports:
          - containerPort: 8000
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 10
  ```
  *(Note: Since you are using Kind, run `kind load docker-image payment-service:v1.0 --name devops-lab` to upload the image into the cluster before applying).*
* **Expected Result:** Manifest deployed to cluster.
* **Checkpoint:** `kubectl get pods -l app=payment-service -n production` returns pods in running and ready status (`1/1` ready).

### [ ] Task 4.4: Expose Service Inter-Networking
* **Why:** Allows pods to discover and communicate with other pods using cluster-internal DNS.
* **Tools/Technologies:** Kubernetes Services.
* **Implementation:** Create Service manifests for all microservices mapping target port 8000 to cluster port 80. Apply configs.
* **Expected Result:** Services active.
* **Checkpoint:** Pinging `http://payment-service.production.svc.cluster.local` from another pod returns successful status codes.

### [ ] Task 4.5: Intentionally Induce Pod Failure & Debug
* **Why:** Builds manual debugging skills using kubectl commands before automation.
* **Tools/Technologies:** Troubleshooting tools (describe, logs).
* **Implementation:** Intentionally trigger a crash by writing a bad environment variable configuration, then run:
  ```powershell
  # Describe pod to see error events
  kubectl describe pod <bad-pod-name> -n production
  # Tail stderr log outputs
  kubectl logs <bad-pod-name> -n production
  ```
* **Expected Result:** Logs display stack trace identifying configuration issues.
* **Checkpoint:** Successfully resolved and restored pod back to Running status.

---

## Phase 5 — Monitoring & Metrics

Deploy Prometheus to collect system and application metrics, and Grafana to visualize health graphs.

### [ ] Task 5.1: Install Prometheus Operator Stack
* **Why:** Deploys Prometheus controllers, scrapers, and alerting dashboards.
* **Tools/Technologies:** Helm, Kube-Prometheus-Stack.
* **Implementation:** Execute helm script:
  ```powershell
  helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
  helm repo update
  helm install monitor prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
  ```
* **Expected Result:** Monitor pods deploy to cluster namespace.
* **Checkpoint:** `kubectl get pods -n monitoring` lists prometheus and grafana instances active.

### [ ] Task 5.2: Configure ServiceScrape Rule targets
* **Why:** Instructs Prometheus to gather custom `/metrics` endpoints from our microservices.
* **Tools/Technologies:** ServiceMonitor Custom Resource Definition (CRD).
* **Implementation:** Create `kubernetes/manifests/servicemonitor.yaml` matching your app label (`app: payment-service`). Apply configuration.
* **Expected Result:** ServiceMonitor registered.
* **Checkpoint:** Accessing Prometheus targets page (`http://localhost:9090` after port forwarding) displays your service endpoint targets as UP.

### [ ] Task 5.3: Build Custom Grafana Dashboard
* **Why:** Provides visual charts tracking system health.
* **Tools/Technologies:** Grafana dashboard JSON models.
* **Implementation:** Port-forward Grafana endpoint:
  ```powershell
  kubectl port-forward svc/monitor-grafana 3000:80 -n monitoring
  ```
  Log in, create a dashboard, and configure panels tracking CPU usage, RAM allocations, latency parameters, and HTTP error metrics.
* **Expected Result:** Dashboard displaying visual metrics panels.
* **Checkpoint:** Trigger load on a microservice; charts display active request spikes.

---

## Phase 6 — Log Aggregation & Parsing

Build utilities to parse raw Kubernetes log files into structured JSON data.

### [ ] Task 6.1: Dump Container Logs
* **Why:** Creates training datasets simulating target production logs.
* **Tools/Technologies:** kubectl log redirection.
* **Implementation:** Export log logs:
  ```powershell
  kubectl logs -l app=payment-service -n production --tail=500 > logs_sandbox.txt
  ```
* **Expected Result:** Text log files created in directory.
* **Checkpoint:** `logs_sandbox.txt` contains timestamped HTTP access log entries.

### [ ] Task 6.2: Design Log Format & Write Parser
* **Why:** Standardizes log lines to prepare them for machine learning inputs.
* **Tools/Technologies:** Python Regular Expressions.
* **Implementation:** Create `src/backend/app/services/log_parser.py`:
  ```python
  import re
  import json

  # Target template: 2026-08-16 03:22:15 [ERROR] payment-service - Database Connection Timeout
  log_pattern = re.compile(
      r"(?P<timestamp>\S+ \S+) \[(?P<level>\w+)\] (?P<service>[a-zA-Z\-]+) - (?P<message>.*)"
  )

  def parse_log_line(line: str) -> dict:
      match = log_pattern.match(line)
      if match:
          return match.groupdict()
      return {"raw": line}
  ```
* **Expected Result:** Parser module created.
* **Checkpoint:** Passing a raw error string returns a dictionary containing keys: `timestamp`, `level`, `service`, `message`.

---

## Phase 7 — ML Anomaly Detection

Train an Isolation Forest model to detect log anomalies using the BGL Supercomputer dataset.

### [ ] Task 7.1: Download and Inspect BGL.log
* **Why:** The BlueGene/L (BGL) log dataset contains normal and alert events, providing a benchmark dataset to train anomaly models.
* **Tools/Technologies:** pandas, urllib.
* **Implementation:** Download the BGL dataset chunk from a public repository, unzip it under `datasets/`, and open using pandas:
  ```python
  import pandas as pd
  # View first 5 rows
  df = pd.read_csv('datasets/BGL_200k.log', sep=' ', header=None, error_bad_lines=False)
  print(df.head())
  ```
* **Expected Result:** Pandas DataFrame loads BGL log columns.
* **Checkpoint:** Confirmed presence of anomaly labels (lines starting with `-` are normal, others indicate alert anomalies).

### [ ] Task 7.2: Feature Engineering
* **Why:** Transforms unstructured logs into a numeric matrix suitable for model training.
* **Tools/Technologies:** scikit-learn CountVectorizer / TfidfVectorizer.
* **Implementation:** Group logs into 5-minute time windows. Extract features:
  1. Count of ERROR/WARNING tokens.
  2. TF-IDF vector of log messages.
  3. Frequency of logs in the window.
* **Expected Result:** Numeric feature matrix `X_train` created.
* **Checkpoint:** Shape of `X_train` is `(number_of_windows, number_of_features)`.

### [ ] Task 7.3: Train Isolation Forest Model
* **Why:** Isolation Forest is an unsupervised algorithm that isolates anomalous log patterns (outliers).
* **Tools/Technologies:** scikit-learn, IsolationForest.
* **Implementation:** Build and train model:
  ```python
  from sklearn.ensemble import IsolationForest
  import joblib

  # contamination=0.02 assumes 2% of the dataset logs are anomalous
  model = IsolationForest(contamination=0.02, random_state=42)
  model.fit(X_train)

  # Save trained weights
  joblib.dump(model, 'src/backend/app/ml/models/anomaly_detector.pkl')
  ```
* **Expected Result:** Model trained and `anomaly_detector.pkl` file saved to disk.
* **Checkpoint:** `model.predict([[95, 91, 510]])` returns `-1` (flagged anomaly outlier) for input variables matching high error rates.

> [!NOTE]
> **Dataset Utilization Strategy:**
> - **BGL Dataset**: Used exclusively offline to train and validate the Isolation Forest model templates.
> - **Real-time logs**: Extracted directly from Kubernetes namespaces and passed through the trained model to detect live production anomalies.

---

## Phase 8 — Incident Management Backend

Construct the OOP-driven FastAPI control-plane service to persist incidents, logs, and actions.

### [ ] Task 8.1: Configure Database Schemas & Migrations
* **Why:** Establishes tables storing SRE data.
* **Tools/Technologies:** SQLAlchemy, Alembic.
* **Implementation:** Define PostgreSQL tables for `Incident` (id, status, service, root_cause), `Action` (id, type, target, approved), and `AuditLog` in `src/backend/app/models/`. Run Alembic migrations:
  ```powershell
  alembic init alembic
  alembic revision --autogenerate -m "Add core tables"
  alembic upgrade head
  ```
* **Expected Result:** Table schemas written to the database.
* **Checkpoint:** Database viewer displays tables `incidents`, `actions`, and `audit_logs`.

### [ ] Task 8.2: Implement REST APIs
* **Why:** Exposes backend CRUD endpoints for the frontend dashboard and agent.
* **Tools/Technologies:** FastAPI routers.
* **Implementation:** Create routers for `/api/v1/incidents` and `/api/v1/actions` in `src/backend/app/api/`.
* **Expected Result:** API endpoints operational.
* **Checkpoint:** Sending a GET request to `/api/v1/incidents` returns an empty array with HTTP 200.

---

## Phase 9 — RAG Knowledge Base

Build a vector search database of Kubernetes manuals, troubleshooting runbooks, and historical incident resolutions.

### [ ] Task 9.1: Assemble DevOps Runbooks
* **Why:** RAG (Retrieval-Augmented Generation) provides contextual runbook documentation to the LLM to improve diagnostic accuracy.
* **Tools/Technologies:** Markdown files.
* **Implementation:** Create troubleshooting guides in `src/rag/data/oom.md` and `src/rag/data/db_timeout.md`:
  ```markdown
  # Runbook: DB Connection Timeout
  Symptom: Payment Service returns HTTP 500. Logs indicate pool exhaustion.
  Solution: Scale the postgres deployment or trigger a rolling restart of payment-service.
  ```
* **Expected Result:** Runbook markdown files saved.
* **Checkpoint:** Confirmed files are saved under `src/rag/data/`.

### [ ] Task 9.2: Generate Embeddings and Save to FAISS Index
* **Why:** Encodes text into vectors to enable semantic similarity searches.
* **Tools/Technologies:** FAISS, LangChain, SentenceTransformers.
* **Implementation:** Write indexer script `src/backend/app/services/indexer.py`:
  ```python
  from langchain_community.document_loaders import DirectoryLoader
  from langchain_text_splitters import RecursiveCharacterTextSplitter
  from langchain_community.vectorstores import FAISS
  from langchain_huggingface import HuggingFaceEmbeddings

  # Load and chunk runbooks
  loader = DirectoryLoader('src/rag/data', glob="*.md")
  docs = loader.load()
  splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
  chunks = splitter.split_documents(docs)

  # Generate vectors and save FAISS index
  db = FAISS.from_documents(chunks, HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2"))
  db.save_local("src/backend/app/rag/faiss_index")
  ```
* **Expected Result:** Vector index database files saved.
* **Checkpoint:** Folder `src/backend/app/rag/faiss_index` contains `index.faiss` and `index.pkl`.

---

## Phase 10 — LLM Integration

Connect the diagnostics pipeline to an LLM (GPT/Llama) using structured templates and output schemas.

### [ ] Task 10.1: Design Diagnostic Prompts with RAG Context
* **Why:** Feeds the LLM with all necessary context (metrics, logs, runbooks, anomaly scores) to generate accurate root-cause analysis reports.
* **Tools/Technologies:** LangChain Prompts.
* **Implementation:** Write a prompt template in `src/backend/app/services/llm_gateway.py`:
  ```python
  from langchain_core.prompts import PromptTemplate

  system_prompt = PromptTemplate.from_template(
      "You are an SRE. Analyze the active incident.\n"
      "Logs: {logs}\n"
      "Metrics: {metrics}\n"
      "Retrained Runbooks: {runbooks}\n"
      "Explain the Root Cause and recommend one safe SRE recovery action."
  )
  ```
* **Expected Result:** Prompt template configured.
* **Checkpoint:** Calling the gateway with mock inputs formats a clean prompt string.

### [ ] Task 10.2: Enforce Structured Output JSON
* **Why:** Ensures the LLM returns structured data that downstream backend engines can parse.
* **Tools/Technologies:** Pydantic validation models.
* **Implementation:** Declare response schema:
  ```python
  from pydantic import BaseModel, Field

  class SREDiagnosis(BaseModel):
      root_cause: str = Field(description="The primary technical cause of the incident")
      confidence: float = Field(description="Confidence score between 0.0 and 1.0")
      action_type: str = Field(description="Must be restart_pod, scale_replicas, or rollback")
      target_service: str = Field(description="The microservice to apply the action to")
  ```
* **Expected Result:** Output constraints configured.
* **Checkpoint:** LLM responses are validated and parsed into the Pydantic model.

---

## Phase 11 — Agentic AI & LangGraph Setup

Model the troubleshooting loop as an AI agent using LangGraph, and implement core operational tools.

### [ ] Task 11.1: Build Agent Tools
* **Why:** Gives the AI agent capabilities to inspect and modify Kubernetes cluster states.
* **Tools/Technologies:** Python, Kubernetes Python SDK.
* **Implementation:** Create core tools in `src/backend/app/agents/tools.py`:
  ```python
  from kubernetes import client, config

  def get_pod_status(namespace: str = "production") -> list:
      config.load_incluster_config()
      v1 = client.CoreV1Api()
      pods = v1.list_namespaced_pod(namespace)
      return [p.status.phase for p in pods.items]
  ```
  Also implement: `get_logs`, `get_metrics`, `restart_service`, `scale_service`, and `rollback_deployment`.
* **Expected Result:** Python tools configured.
* **Checkpoint:** Executing `get_pod_status()` returns list of active pod phases.

### [ ] Task 11.2: Construct LangGraph State machine
* **Why:** Manages the agent's decision flow, allowing it to transition between inspection, diagnosis, execution, and verification states.
* **Tools/Technologies:** LangGraph.
* **Implementation:** Map nodes and edges in `src/backend/app/agents/graph.py`:
  ```python
  from langgraph.graph import StateGraph, END
  # Initialize State Graph
  workflow = StateGraph(SREAgentState)
  workflow.add_node("scrape", scrape_node)
  workflow.add_node("diagnose", diagnose_node)
  workflow.add_node("execute", execute_node)

  workflow.add_edge("scrape", "diagnose")
  workflow.add_conditional_edges("diagnose", route_action)
  ```
* **Expected Result:** Graph layout compiled.
* **Checkpoint:** Calling the graph runs the scraper node followed by the diagnosis node.

> [!IMPORTANT]
> **Tool Selection Logic:**
> The agent determines tool selection by mapping LLM diagnosis outputs to its registered tools schema list. If the LLM indicates `action_type = "restart_pod"`, the agent schedules the `restart_service` tool.

---

## Phase 12 — Self-Healing Loop

Implement the closed-loop self-healing cycle: **Detect → Investigate → Analyze → Decide → Validate → Execute → Verify**.

### [ ] Task 12.1: Enforce Security Policies
* **Why:** Protects the cluster from unsafe commands or parameter injections.
* **Tools/Technologies:** Allowlist validation functions.
* **Implementation:** Implement strict policy checks in `src/backend/app/services/policy.py`:
  ```python
  def validate_agent_action(action: dict) -> bool:
      # Allowlist checks
      ALLOWED_ACTIONS = ["restart_pod", "scale_replicas", "rollback_deployment"]
      if action.get("type") not in ALLOWED_ACTIONS:
          return False
      # Parameter validation: block characters that could lead to command injection
      target = action.get("target", "")
      if any(char in target for char in [";", "&", "|", "$"]):
          return False
      return True
  ```
* **Expected Result:** Policy checks configured.
* **Checkpoint:** Passing an action payload containing `type: "delete_namespace"` returns `False` (action blocked).

### [ ] Task 12.2: Implement Closed-Loop Verification
* **Why:** Confirms whether the recovery action successfully restored service health.
* **Tools/Technologies:** Metrics checking functions.
* **Implementation:** Code verification check:
  1. Wait 20 seconds for the pod rollout to complete.
  2. Query Prometheus API for HTTP error rates of the target service.
  3. If error rates are below 1%, mark the incident as RESOLVED.
  4. If error rates remain high, rollback the action and escalate to human SREs.
* **Expected Result:** Verification loop operational.
* **Checkpoint:** If verification metrics remain abnormal, the state transitions to `FAILED`.

---

## Phase 13 — Failure Simulation

Trigger controlled outages inside the cluster to validate your monitoring and agent pipelines.

### [ ] Task 13.1: Simulate Memory Exhaustion (OOMKilled)
* **Why:** Validates that Kubernetes triggers OOM events, Prometheus fires alerts, and the agent detects memory issues.
* **Tools/Technologies:** Kubernetes Resource Limits, stress test scripts.
* **Implementation:** Add resource limits to a service manifest:
  ```yaml
  resources:
    limits:
      memory: "64Mi"
  ```
  Expose a `/stress-memory` endpoint in the service that appends items to a list in an infinite loop to trigger an out-of-memory error.
* **Expected Result:** Pod crashes with status `OOMKilled`.
* **Checkpoint:** Running `kubectl get pods -n production` displays `OOMKilled` in the reason field.

### [ ] Task 13.2: Simulate Database Connection Pool Exhaustion
* **Why:** Creates a cascading timeout error to verify that RAG and LLM diagnostic prompts can trace errors back to database issues.
* **Tools/Technologies:** Database connection limits.
* **Implementation:** Set `max_connections = 5` in the PostgreSQL database configuration, and simulate concurrent API connections to exhaust the connection pool.
* **Expected Result:** Microservice logs display connection pool timeout exceptions.
* **Checkpoint:** Microservice HTTP health-checks return HTTP 500.

---

## Phase 14 — Frontend Dashboard

Build a React dashboard displaying cluster health metrics, active incidents, and LLM diagnostic reports.

### [ ] Task 14.1: Render Microservice Health Panel
* **Why:** Provides operators with a clear view of service statuses, active anomalies, and open incidents.
* **Tools/Technologies:** React, Tailwind CSS / Vanilla CSS.
* **Implementation:** Build components for:
  - Metric status charts (CPU/RAM).
  - Anomaly status indicators.
  - Active incidents grid with diagnostic details (Root Cause, Action, Confidence Score).
* **Expected Result:** React UI components configured.
* **Checkpoint:** Dashboard displays active incidents fetched from the backend API.

### [ ] Task 14.2: Implement Chat Assistant Interface
* **Why:** Enables users to query system health using natural language (e.g. "Why is payment-service slow?").
* **Tools/Technologies:** React chat layouts.
* **Implementation:** Implement a chat client that forwards queries to the backend LLM gateway. The gateway retrieves metrics, logs, and RAG contexts, returning a natural-language SRE explanation.
* **Expected Result:** Chat interface integrated.
* **Checkpoint:** Sending a message returns a detailed explanation of service latency.

---

## Phase 15 — CI/CD Pipeline

Configure automated build and deployment pipelines to track changes and rollbacks.

### [ ] Task 15.1: Create GitHub Actions Workflow
* **Why:** Automates code checks, packages fresh Docker images, and deploys configurations to Kubernetes.
* **Tools/Technologies:** GitHub Actions.
* **Implementation:** Create `.github/workflows/deploy.yaml` to run tests and build/deploy containers to the cluster.
* **Expected Result:** CI/CD pipeline configured.
* **Checkpoint:** Pushing commits triggers the build pipeline, deploying the updated containers.

---

## Phase 16 — Production Security Guardrails

Implement role-based access controls and action confirmation policies.

### [ ] Task 16.1: Enforce Human-in-the-Loop Confirmation
* **Why:** Prevents the AI agent from executing risky actions without approval, protecting production environments from hallucinations.
* **Tools/Technologies:** Manual approvals databases.
* **Implementation:** Set validation flags:
  ```python
  # Set action state to pending approval
  if action_risk == "high":
      action.status = "PENDING_APPROVAL"
      notify_operator(action)
  ```
* **Expected Result:** Action queue paused, waiting for operator confirmation.
* **Checkpoint:** High-risk actions require manual confirmation via the React UI before execution.

---

## Phase 17 — Testing Suite

Create a testing suite to validate all system modules.

### [ ] Task 17.1: Write Integration Tests for Recovery Loop
* **Why:** Validates that the end-to-end self-healing loop resolves incidents correctly.
* **Tools/Technologies:** pytest, mock requests.
* **Implementation:** Create `tests/test_recovery.py` simulating an incident triggers, the agent runs, the action is validated, and the system resolves.
* **Expected Result:** pytest run executes successfully.
* **Checkpoint:** Run `pytest tests/test_recovery.py` in terminal passes all assertions.

---

## Phase 18 — Production Optimization

Improve system performance and reliability under heavy loads.

### [ ] Task 18.1: Configure Redis Caching & Queue Worker
* **Why:** Minimizes database latency and offloads background agent runs from main API threads.
* **Tools/Technologies:** Redis, Celery.
* **Implementation:** Initialize Celery workers and store metrics in Redis.
* **Expected Result:** Background jobs processed correctly by Celery task workers.
* **Checkpoint:** Incident creation dispatches background tasks, returning instant API responses.

---

## Phase 19 — Cloud Deployment

Deploy the system to a production cloud environment.

### [ ] Task 19.1: Deploy to Cloud Kubernetes (EKS / GKE)
* **Why:** Transition from local Kind namespaces to production cloud clusters.
* **Tools/Technologies:** AWS EKS, GCP GKE.
* **Implementation:** Create cluster resources using Terraform, deploy microservices, and configure public load balancers.
* **Expected Result:** Cluster running in the cloud.
* **Checkpoint:** Microservice URLs load correctly from public domain paths.

---

## Phase 20 — Final Project & Handover

Compile system diagrams, database documentation, and run evaluations.

### [ ] Task 20.1: Compile Systems Handover Manual
* **Why:** Consolidates system details to make the codebase easy to maintain.
* **Tools/Technologies:** Markdown.
* **Implementation:** Document:
  - Database Entity Relationship (ER) diagrams.
  - API endpoint documentations.
  - Agent state machines and tools configurations.
* **Expected Result:** Final README file written.
* **Checkpoint:** Master setup guide is fully documented.

---

## Master Checklist: Chronological Action Order

1. [ ] Create project planning architecture model.
2. [ ] Map out microservices routes.
3. [ ] Define workspace folder layouts.
4. [ ] Install Helm, Git, and Docker.
5. [ ] Initialize Python Virtualenv.
6. [ ] Spin up local Kind cluster.
7. [ ] Verify kubectl context config.
8. [ ] Scaffold 4 FastAPI microservices.
9. [ ] Create local PostgreSQL container.
10. [ ] Package apps into Dockerfiles.
11. [ ] Build and tag v1.0 Docker images.
12. [ ] Load images into Kind cluster.
13. [ ] Deploy Stateful Postgres to Kind.
14. [ ] Deploy stubs with Readiness/Liveness probes.
15. [ ] Expose internal K8s Services.
16. [ ] Install Kube-Prometheus stack via Helm.
17. [ ] Map ServiceMonitor to scraped endpoints.
18. [ ] Setup Grafana monitoring charts.
19. [ ] Write log parsing python scripts.
20. [ ] Preprocess BGL log dataset.
21. [ ] Extract numeric TF-IDF features.
22. [ ] Train Isolation Forest outlier detector.
23. [ ] Configure PostgreSQL tables with Alembic.
24. [ ] Build incidents and actions backend APIs.
25. [ ] Document markdown runbooks for RAG.
26. [ ] Index documents into FAISS vector database.
27. [ ] Code prompt template gateways.
28. [ ] Standardize LLM responses into Pydantic models.
29. [ ] Create K8s python client tools.
30. [ ] Map nodes to LangGraph state machine.
31. [ ] Code strict policy allowlist checkers.
32. [ ] Build post-action verification metrics monitor.
33. [ ] Simulate pod memory OOM crashes.
34. [ ] Simulate DB connection exhaust exceptions.
35. [ ] Build React monitoring UI cards.
36. [ ] Implement SRE chat assistant interface.
37. [ ] Build GitHub Actions CI/CD workflows.
38. [ ] Enforce human approval validation checks.
39. [ ] Write pytest integration suites.
40. [ ] Deploy Redis metrics caches.
41. [ ] Setup Celery background task workers.
42. [ ] Deploy microservices to AWS/GCP cloud environments.
43. [ ] Write final handover README documentation.
