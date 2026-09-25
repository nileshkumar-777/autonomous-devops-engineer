/* ==========================================================================
   Autonomous DevOps SRE Dashboard JavaScript Logic (app_v5.js)
   ========================================================================== */

// 1. Core Roadmap Data Structure (All 10 phases and sub-tasks)
const roadmapData = [
    {
        id: "phase-1",
        num: 1,
        category: "cat-a",
        categoryName: "Infrastructure & Observability",
        title: "Phase 1: DevOps Foundation",
        description: "Set up the local Kubernetes workspace, Dockerize 3-4 microservices, and configure basic service networking.",
        tasks: [
            {
                id: "t1-1",
                title: "Provision Local Kubernetes Cluster",
                desc: "Install Docker Desktop followed by either Kind or Minikube. Verify cluster control path access.",
                code: "# Install Kind cluster\nkind create cluster --name devops-lab\n# Verify cluster node status\nkubectl get nodes",
                outcome: "A single-node cluster is online and responding to kubectl queries.",
                tag: "Setup"
            },
            {
                id: "t1-2",
                title: "Develop Scaffolds for Microservices",
                desc: "Create simple API stubs for user-service, payment-service, and order-service using FastAPI.",
                code: "# Scaffold layout\nmkdir -p src/microservices/payment-service/app\ntouch src/microservices/payment-service/app/main.py",
                outcome: "Basic FastAPI codebases that return mocked HTTP responses.",
                tag: "App Dev"
            },
            {
                id: "t1-3",
                title: "Dockerize Services & Deploy to K8s",
                desc: "Write Dockerfiles for each service, build local images, and deploy them using Kubernetes deployment manifests.",
                code: "# Build Docker Image\ndocker build -t local/payment-service:v1.0 ./src/microservices/payment-service\n# Deploy resources\nkubectl apply -f src/kubernetes/manifests/",
                outcome: "All pods are in RUNNING status inside the 'production' namespace.",
                tag: "Deployment"
            }
        ]
    },
    {
        id: "phase-2",
        num: 2,
        category: "cat-a",
        categoryName: "Infrastructure & Observability",
        title: "Phase 2: Observability & Metrics",
        description: "Deploy Prometheus and Grafana, instrument microservices with metrics middleware, and design visual dashboards.",
        tasks: [
            {
                id: "t2-1",
                title: "Install Prometheus & Grafana via Helm",
                desc: "Install the Prometheus stack inside your local cluster to scrape system and pod level metrics.",
                code: "# Add Helm repo\nhelm repo add prometheus-community https://prometheus-community.github.io/helm-charts\nhelm repo update\n# Install stack\nhelm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace",
                outcome: "Prometheus operator and Grafana pods are successfully running.",
                tag: "K8s Setup"
            },
            {
                id: "t2-2",
                title: "Instrument Microservices for Scrapes",
                desc: "Integrate prometheus-client middleware in FastAPI services to expose request counts, latency, and error counts on /metrics.",
                code: "from prometheus_fastapi_instrumentator import Instrumentator\n\n@app.on_event(\"startup\")\ndef startup():\n    Instrumentator().instrument(app).expose(app)",
                outcome: "Curated metrics are readable by accessing http://localhost:8000/metrics.",
                tag: "Instrumentation"
            },
            {
                id: "t2-3",
                title: "Configure Custom Grafana Observability Dashboard",
                desc: "Import a dashboard JSON configuring charts for CPU/Memory, latency distribution, and error rates by service.",
                code: "# Port forward Grafana to view locally\nkubectl port-forward svc/prometheus-grafana 8080:80 -n monitoring",
                outcome: "Visual charts live-updating as traffic triggers request changes.",
                tag: "Observability"
            }
        ]
    },
    {
        id: "phase-3",
        num: 3,
        category: "cat-a",
        categoryName: "Infrastructure & Observability",
        title: "Phase 3: Log Collection & Centralization",
        description: "Gather logs from Kubernetes components and local applications. Develop an initial parsing script.",
        tasks: [
            {
                id: "t3-1",
                title: "Extract Pod Logs via Shell",
                desc: "Write scripts that poll and aggregate standard output logs from all running microservices.",
                code: "# Dump last 100 log lines of payment service to file\nkubectl logs --tail=100 -l app=payment-service -n production > payment.log",
                outcome: "Aggregated raw application logs written to files or stdout streams.",
                tag: "Logging"
            },
            {
                id: "t3-2",
                title: "Write Regex Log Parser in Python",
                desc: "Implement a parser converting raw logs to structured JSON elements containing level, component, message, and timestamp.",
                code: "import re\n# Regex pattern to match timestamp and level\nlog_pattern = re.compile(r'(?P<time>\\S+ \\S+) \\[(?P<level>\\w+)\\] (?P<msg>.*)')",
                outcome: "A utility function that transforms unstructured lines into dictionary-based data.",
                tag: "Parser"
            },
            {
                id: "t3-3",
                title: "Generate Database Failure & Capture Cascade",
                desc: "Intentionally shut down the database service and observe metric and log outputs across dependency chains.",
                code: "# Stop database deployment\nkubectl scale deployment postgres --replicas=0 -n production\n# Fetch payment logs to check connection issues\nkubectl logs -l app=payment-service -n production",
                outcome: "Recorded log of cascading timeouts and elevated HTTP 5xx error metrics.",
                tag: "SRE Lab"
            }
        ]
    },
    {
        id: "phase-4",
        num: 4,
        category: "cat-b",
        categoryName: "AI & ML Foundation",
        title: "Phase 4: Anomaly Detector",
        description: "Parse the BGL Supercomputer log dataset, extract log signature features, and train an Isolation Forest model.",
        tasks: [
            {
                id: "t4-1",
                title: "Preprocess BGL.log Dataset",
                desc: "Load chunks of BGL.log, parse headers, and map them to structural tokens.",
                code: "# Extract basic statistics from BGL log\nhead -n 5 BGL.log\n# Run parsing script to output csv\npython parse_bgl.py --input BGL.log --output bgl_structured.csv",
                outcome: "A cleaned, structured dataset of historical supercomputer error states.",
                tag: "ML Pipeline"
            },
            {
                id: "t4-2",
                title: "Feature Engineering & Extraction",
                desc: "Transform parsed logs into fixed-time windows with features (error log rate, log frequency, message signature indexes).",
                code: "# Vectorizing messages using TF-IDF or count vectors\nfrom sklearn.feature_extraction.text import TfidfVectorizer\nvectorizer = TfidfVectorizer(max_features=100)",
                outcome: "A feature matrix ready to feed into anomaly training models.",
                tag: "Feature Eng"
            },
            {
                id: "t4-3",
                title: "Train Isolation Forest Detector",
                desc: "Build an unsupervised Isolation Forest model to flag anomalous log patterns and host it as a FastAPI endpoint.",
                code: "from sklearn.ensemble import IsolationForest\nclf = IsolationForest(contamination=0.01)\nclf.fit(X_train)\n# Save model weights\nimport joblib\njoblib.dump(clf, 'anomaly_detector.pkl')",
                outcome: "A REST API returning classification scores and normal/anomaly flags.",
                tag: "Modeling"
            }
        ]
    },
    {
        id: "phase-5",
        num: 5,
        category: "cat-b",
        categoryName: "AI & ML Foundation",
        title: "Phase 5: Backend OOP Architecture (FastAPI + SQL + Cache)",
        description: "Develop the FastAPI control-plane backend utilizing object-oriented patterns, PostgreSQL databases, and Redis caches.",
        tasks: [
            {
                id: "t5-1",
                title: "Create OOP Service Abstractions",
                desc: "Design abstract monitoring, database access, and alert handling classes following SOLID principles.",
                code: "class AbstractMonitor(ABC):\n    @abstractmethod\n    def fetch_metrics(self) -> List[Metric]: pass",
                outcome: "Robust modular code system allowing easy swapping between Mock and Real components.",
                tag: "OOP Design"
            },
            {
                id: "t5-2",
                title: "Implement PostgreSQL Database Schemas",
                desc: "Configure SQLAlchemy/Alembic migrations for tables: incidents, metrics, actions, and deployments.",
                code: "# Run alembic migrations to establish DB schema\nalembic upgrade head",
                outcome: "Functional database tables supporting relation constraints for incident reports.",
                tag: "Database"
            },
            {
                id: "t5-3",
                title: "Integrate Redis Cache for Telemetry Data",
                desc: "Use Redis to buffer live container metrics and lock agent runs preventing concurrent execution conflicts.",
                code: "import redis\nr = redis.Redis(host='localhost', port=6379)\n# Store transient metrics with TTL\nr.setex('telemetry:payment', 60, json_data)",
                outcome: "Sub-millisecond data reads for active SRE telemetry dashboards.",
                tag: "Caching"
            }
        ]
    },
    {
        id: "phase-6",
        num: 6,
        category: "cat-b",
        categoryName: "AI & ML Foundation",
        title: "Phase 6: RAG Knowledge Base",
        description: "Build an index of system runbooks, K8s documents, and AWS guides using vector embeddings and FAISS / Chroma DB.",
        tasks: [
            {
                id: "t6-1",
                title: "Document Collection & Chunking",
                desc: "Gather internal PDF/Markdown runbooks, divide them into 500-token chunks with overlap.",
                code: "# Code chunking sample\ntext_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)",
                outcome: "A database of indexed text snippets relating to typical outage symptoms.",
                tag: "RAG Pipeline"
            },
            {
                id: "t6-2",
                title: "Generate Embeddings & Save to FAISS",
                desc: "Process chunks via standard sentence transformers and save the indexing vector matrix locally.",
                code: "from langchain_community.vectorstores import FAISS\nfrom langchain_openai import OpenAIEmbeddings\n\ndb = FAISS.from_documents(docs, OpenAIEmbeddings())",
                outcome: "A vector database ready to accept semantic searches for system errors.",
                tag: "Vector DB"
            },
            {
                id: "t6-3",
                title: "Create Search API for Runbooks",
                desc: "Expose an endpoint that takes an error string (e.g. 'OOMKilled') and returns the top 3 relevant runbook sections.",
                code: "# Query the database\nresults = db.similarity_search(\"CrashLoopBackOff database connection timeout\")",
                outcome: "Accurate runbook retrieval containing debugging commands mapped to symptoms.",
                tag: "Search API"
            }
        ]
    },
    {
        id: "phase-7",
        num: 7,
        category: "cat-b",
        categoryName: "AI & ML Foundation",
        title: "Phase 7: LLM Diagnostic Reasoner",
        description: "Implement GPT/Llama models to analyze logs, metrics, and retrieved runbooks to produce a Root Cause Analysis report.",
        tasks: [
            {
                id: "t7-1",
                title: "Design Prompts for Root Cause Analysis",
                desc: "Write system prompts that take telemetry inputs, raw logs, active deployments, and RAG guidelines to formulate answers.",
                code: "Prompt: You are an expert SRE. Given the logs [LOGS] and runbook [RUNBOOK], identify the exact cause and list recommended actions.",
                outcome: "A highly structured prompt engineered to prevent model hallucinations.",
                tag: "Prompt Eng"
            },
            {
                id: "t7-2",
                title: "Call LLM API and Parse Responses",
                desc: "Integrate LLM API clients, parse response fields into Pydantic models for JSON standardization.",
                code: "class Diagnosis(BaseModel):\n    root_cause: str\n    confidence: float\n    recommended_action: str",
                outcome: "Predictable API output structures that downstream control systems can validate.",
                tag: "Integration"
            },
            {
                id: "t7-3",
                title: "Combine Observability Outputs for Diagnostics",
                desc: "Create an orchestration pipeline assembling ML flags, K8s events, and LLM text reports into a unified analyzer.",
                code: "# Run diagnostic report endpoint\nGET /api/v1/incidents/{incident_id}/diagnose",
                outcome: "Comprehensive SRE reports listing evidence details, root cause, and recovery path.",
                tag: "RCA Engine"
            }
        ]
    },
    {
        id: "phase-8",
        num: 8,
        category: "cat-c",
        categoryName: "Orchestration & Production",
        title: "Phase 8: LangGraph AI Agent Core",
        description: "Model the autonomous troubleshooting loop as a state machine using LangGraph. Implement SRE tools.",
        tasks: [
            {
                id: "t8-1",
                title: "Map SRE Graph States",
                desc: "Define nodes (Check Pod Status, Read Logs, Query RAG, Diagnose, Call Executor) and directional edges representing graphs.",
                code: "builder = StateGraph(SREAgentState)\nbuilder.add_node(\"diagnose\", diagnose_node)\nbuilder.add_edge(\"diagnose\", \"execute_actions\")",
                outcome: "A formal state machine regulating the flow of analysis and actions.",
                tag: "LangGraph"
            },
            {
                id: "t8-2",
                title: "Expose Kubernetes SDK Agent Tools",
                desc: "Write Python tool helper functions wrapping the official Kubernetes SDK to read logs, fetch metrics, and query namespace states.",
                code: "from kubernetes import client, config\n# Load in-cluster config\nconfig.load_incluster_config()\nv1 = client.CoreV1Api()\npods = v1.list_namespaced_pod(namespace=\"production\")",
                outcome: "Secure, structured Python functions registered as LLM agent tools.",
                tag: "Tool Dev"
            },
            {
                id: "t8-3",
                title: "Implement Loop Decisions & Routing Nodes",
                desc: "Configure conditional routing inside LangGraph to decide if further diagnostics are required or if we can run actions.",
                code: "def should_continue(state):\n    if state[\"confidence\"] > 0.8: return \"run_fix\"\n    return \"get_more_logs\"",
                outcome: "Self-correcting agent chains that request additional metrics if diagnostic confidence is low.",
                tag: "Routing"
            }
        ]
    },
    {
        id: "phase-9",
        num: 9,
        category: "cat-c",
        categoryName: "Orchestration & Production",
        title: "Phase 9: Self-Healing & Policy Validator",
        description: "Implement safety validation for agent recommendations and close the loop by verifying recovery metrics.",
        tasks: [
            {
                id: "t9-1",
                title: "Build SRE Tool Execution Policies",
                desc: "Implement a policy validator restricting dangerous commands (like deleting database namespaces) and allowlisting safe commands.",
                code: "def validate_action(action: dict) -> bool:\n    allowed = [\"restart_pod\", \"rollback_deployment\", \"scale_replicas\"]\n    return action.get(\"type\") in allowed",
                outcome: "A safety layer that rejects arbitrary commands generated by the LLM.",
                tag: "Security"
            },
            {
                id: "t9-2",
                title: "Implement Action Execution Handlers",
                desc: "Implement actual REST API or RPC command structures calling K8s to scale services or trigger rolling restarts.",
                code: "# Restart deployment\nv1.patch_namespaced_deployment(name=service_name, namespace=ns, body=restart_body)",
                outcome: "Direct cluster state modifications executed safely by the API backend.",
                tag: "Execution"
            },
            {
                id: "t9-3",
                title: "Code Automated Verification Loops",
                desc: "Develop post-execution metrics monitors that wait 30-60 seconds, check error rates, and verify if the system has recovered.",
                code: "# Check latency has decreased after restart\nfor i in range(5):\n    metrics = fetch_latest_metrics()\n    if metrics.error_rate < 0.01: return \"RESOLVED\"\n    time.sleep(10)",
                outcome: "A verified closed-loop SRE controller that repeats diagnosis if recovery checks fail.",
                tag: "Verification"
            }
        ]
    },
    {
        id: "phase-10",
        num: 10,
        category: "cat-c",
        categoryName: "Orchestration & Production",
        title: "Phase 10: Production Dashboards & CI/CD",
        description: "Add user authentication, role-based access control, detailed auditing logs, CI/CD pipes, and build a full React interface.",
        tasks: [
            {
                id: "t1-a",
                title: "Build the React SRE Dashboard UI",
                desc: "Implement a dynamic interface showing service health, real-time anomalies, open incidents, and the AI agent's execution graphs.",
                code: "// React API call fetching open incidents\nconst fetchIncidents = async () => {\n  const res = await fetch('/api/incidents');\n  setIncidents(await res.json());\n}",
                outcome: "A clean user interface showing live alert notifications and recovery logs.",
                tag: "Frontend"
            },
            {
                id: "t1-b",
                title: "Implement RBAC & Incident Audit Logs",
                desc: "Add user roles (Admin vs Operator) requiring human approval for rolling back core deployments. Store every action in an immutable audit ledger.",
                code: "# Database entry capturing audit trail\nINSERT INTO audit_logs (operator, action, timestamp, approved_by) VALUES (...)",
                outcome: "A secure framework tracing exactly which model or user initiated infrastructure changes.",
                tag: "Security"
            },
            {
                id: "t1-c",
                title: "Design CI/CD GitHub Actions Workflow",
                desc: "Build pipeline building code Docker files, running unit checks, and triggering rolling deployments while notifying the SRE agent.",
                code: "# GitHub actions file snippet\n- name: Build and Push\n  uses: docker/build-push-action@v2\n  with:\n    tags: payment-service:latest",
                outcome: "A continuous delivery chain that links microservice versions with active alerts.",
                tag: "CI/CD"
            }
        ]
    }
];

// 2. Chronological step-by-step pipeline data
const setupTimelineSteps = [
    {
        id: "s-1",
        num: 1,
        phaseTag: "Phase 1: Core Cluster",
        title: "Provision Local Kubernetes Cluster & Namespace",
        desc: "Boot up Docker and initialize a Kubernetes control plane workspace locally using Kind or Minikube. Setup the baseline target deployment namespace.",
        code: "# Create cluster workspace using Kind\nkind create cluster --name devops-lab\n# Establish the target deployment namespace\nkubectl create namespace production",
        outcome: "A single-node cluster is online and responding to kubectl namespace checks."
    },
    {
        id: "s-2",
        num: 2,
        phaseTag: "Phase 5: Database Layer",
        title: "Deploy PostgreSQL Persistent Database",
        desc: "Deploy a PostgreSQL server pod using declarative YAML manifests. This acts as the storage system for incident logs, audit ledgers, and metrics benchmarks.",
        code: "# Deploy PostgreSQL instance in target namespace\nkubectl apply -f src/kubernetes/manifests/postgres.yaml\n# Check pod runtime state\nkubectl get pods -n production | grep postgres",
        outcome: "A functional database service exposing port 5432 is live."
    },
    {
        id: "s-3",
        num: 3,
        phaseTag: "Phase 5: Caching Layer",
        title: "Deploy Redis Cache Node",
        desc: "Deploy a Redis cache server inside the cluster. It locks active SRE analysis cycles to prevent race conditions and buffers transient telemetry metric scrapes.",
        code: "# Apply Redis service deployment config\nkubectl apply -f src/kubernetes/manifests/redis.yaml\n# Verify Redis service endpoint registry\nkubectl get svc -n production | grep redis",
        outcome: "Redis pod is running, accepting socket requests on port 6379."
    },
    {
        id: "s-4",
        num: 4,
        phaseTag: "Phase 1: App Execution",
        title: "Build & Deploy FastAPI Microservice Stubs",
        desc: "Dockerize FastAPI user, payment, and order services. Push images to the local registry and execute deployment manifests to launch them within Kubernetes.",
        code: "# Packaging stubs\ndocker build -t local/payment-service:v1.0 ./src/microservices/payment-service\n# Rollout microservices in namespace\nkubectl apply -f src/kubernetes/manifests/payment-deployment.yaml",
        outcome: "API pods scale up successfully, resolving DNS entries locally."
    },
    {
        id: "s-5",
        num: 5,
        phaseTag: "Phase 2: Monitoring Infra",
        title: "Install Prometheus & Grafana Operators",
        desc: "Deploy the Prometheus operator stack via Helm inside a monitoring namespace. This sets up metric scraper controllers and Grafana visual charts.",
        code: "# Add Helm Charts Repository\nhelm repo add prometheus-community https://prometheus-community.github.io/helm-charts\nhelm repo update\n# Install monitoring stack\nhelm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace",
        outcome: "Prometheus daemons start scraping node and system level metrics."
    },
    {
        id: "s-6",
        num: 6,
        phaseTag: "Phase 2: App Metrics",
        title: "Instrument Microservices & Validate /metrics Exporter",
        desc: "Integrate standard Prometheus middleware instrumentation inside FastAPI stubs, exposing application HTTP error rates and response durations on `/metrics`.",
        code: "# Test metrics API exposure locally\ncurl http://localhost:8000/metrics | grep http_requests_total",
        outcome: "Prometheus scrapes endpoints successfully, collecting request metrics."
    },
    {
        id: "s-7",
        num: 7,
        phaseTag: "Phase 3 & 4: Data pipeline",
        title: "Collect Sandbox Logs & Extract Feature Vectors",
        desc: "Develop logging capture utilities. Gather raw standard output log lines from the container clusters and parse them into structured CSV rows.",
        code: "# Query pod standard logs\nkubectl logs -l app=payment-service -n production > raw_events.log\n# Transform log data\npython parse_bgl.py --input raw_events.log --output parsed.csv",
        outcome: "Unstructured strings mapped to CSV features (timestamps, levels, tokens)."
    },
    {
        id: "s-8",
        num: 8,
        phaseTag: "Phase 4: ML Modeling",
        title: "Train Isolation Forest Anomaly Detection Model",
        desc: "Train an unsupervised Isolation Forest model using scikit-learn on the parsed log features to output anomaly scoring. Save model weights as file pickles.",
        code: "from sklearn.ensemble import IsolationForest\nimport joblib\n# Fit dataset features\nclf = IsolationForest(contamination=0.02, random_state=42)\nclf.fit(X_train)\njoblib.dump(clf, 'anomaly_detector.pkl')",
        outcome: "FastAPI anomaly score model output returns -1 outlier flags."
    },
    {
        id: "s-9",
        num: 9,
        phaseTag: "Phase 6: Knowledge Base",
        title: "Index Troubleshooting Runbooks in FAISS Vector DB",
        desc: "Gather SRE recovery runbooks, segment them into dense token chunks, encode them using sentence transformers, and save index vectors to a FAISS database.",
        code: "# Compile RAG vector database index\npython index_runbooks.py --docs ./runbooks/ --db ./faiss_index/",
        outcome: "Semantic query search successfully returns top runbook paragraphs."
    },
    {
        id: "s-10",
        num: 10,
        phaseTag: "Phase 7: Diagnostic LLM",
        title: "Configure Prompt Templates & Integrate LLM Gateway",
        desc: "Construct system prompt scripts mapping logs, metrics context, and RAG guidelines. Call LLM chat endpoints, parsing output structures to JSON.",
        code: "prompt = PromptTemplate.from_template(\n    \"Context logs: {logs}\\nRunbooks: {runbooks}\\n\"\n    \"Identify the root cause and output JSON matching the schema.\"\n)",
        outcome: "LLM responses return root causes with high confidence metrics."
    },
    {
        id: "s-11",
        num: 11,
        phaseTag: "Phase 8: LangGraph Core",
        title: "Map LangGraph Troubleshooting State Nodes & Edges",
        desc: "Establish the StateGraph schema. Program core nodes (scraper, search vectors, diagnose, policy check, execute, verify) and link conditional routes.",
        code: "builder = StateGraph(SREAgentState)\nbuilder.add_node(\"scraper\", scrape_node)\nbuilder.add_conditional_edges(\"verifier\", route_next)",
        outcome: "LangGraph engine compiled and verified executing sequentially."
    },
    {
        id: "s-12",
        num: 12,
        phaseTag: "Phase 9 & 10: Loop Closure",
        title: "Implement Policy Guardrails, Executions, & React UI",
        desc: "Add strict policy filters (restarts/rollbacks allowlist) to reject arbitrary commands. Call K8s client to apply fixes and build the React frontend.",
        code: "def validate_action(action: dict) -> bool:\n    return action.get(\"type\") in [\"restart_pod\", \"rollback_deployment\"]",
        outcome: "React UI displays status maps and progress tracker."
    }
];

// 3. Complete 21-phase master checklist data (Phases 0 to 20)
const flowGuidePhases = [
    {
        id: "fg-p0",
        num: 0,
        category: "cat-a",
        title: "Phase 0 — Project Planning",
        description: "Draft architecture frameworks, resource maps, and safety allowlist boundaries before coding.",
        tasks: [
            { id: "fg-0-1", title: "Map Out Complete System Topology", why: "Resolves data interaction dependencies.", tech: "Mermaid, Draw.io", impl: "Review the system block schemas linking UI to K8s layers.", outcome: "Defined APIs mapping gateway parameters.", checkpoint: "All 5 SRE flow diagrams approved." },
            { id: "fg-0-2", title: "Establish Microservices Specifications", why: "Clarifies stub requirements.", tech: "FastAPI Specifications", impl: "Define routes for Order, User, Payment, and Notification services.", outcome: "REST path contracts defined.", checkpoint: "Routes doc saved to specs database." },
            { id: "fg-0-3", title: "Design Safe Execution Policy Allowlists", why: "Blocks unauthorized model container mutations.", tech: "YAML security configurations", impl: "Restrict LLM outputs to restart_pod, scale_replicas, and rollback.", outcome: "Allowlist boundaries declared.", checkpoint: "Arbitrary shell injection execution declared blocked." }
        ]
    },
    {
        id: "fg-p1",
        num: 1,
        category: "cat-a",
        title: "Phase 1 — Development Environment",
        description: "Provision local cluster configurations, install CLI helpers, and organize repository trees.",
        tasks: [
            { id: "fg-1-1", title: "Install CLI binaries via package manager", why: "Prepares orchestration tools.", tech: "Helm, Git, Kind, Kubectl", impl: "run choco install kubernetes-cli helm git kind -y", outcome: "Executable shell binaries added to user path.", checkpoint: "helm version exits with code 0." },
            { id: "fg-1-2", title: "Create local Kind Kubernetes Cluster", why: "Spins up target container lab.", tech: "Kind config, Docker desktop", impl: "kind create cluster --name devops-lab", outcome: "devops-lab-control-plane node starts running in Docker.", checkpoint: "kubectl get nodes returns node in Ready state." },
            { id: "fg-1-3", title: "Scaffold Git directory folder structures", why: "Organizes source namespaces.", tech: "Git CLI, PowerShell scripts", impl: "mkdir -p src/microservices src/backend src/ml src/rag kubernetes/manifests", outcome: "Workspace directories created on disk.", checkpoint: "git init is executed and development branch created." }
        ]
    },
    {
        id: "fg-p2",
        num: 2,
        category: "cat-a",
        title: "Phase 2 — Sample Microservices",
        description: "Construct the four FastAPI stubs and verify health endpoints.",
        tasks: [
            { id: "fg-2-1", title: "Code API stubs with health check endpoints", why: "Provides targets for incident simulator.", tech: "Python, FastAPI, Uvicorn", impl: "Create src/microservices/payment-service/app/main.py returning healthy states.", outcome: "FastAPI server script compiled.", checkpoint: "uvicorn main:app runs locally on port 8000 returning HTTP 200." },
            { id: "fg-2-2", title: "Setup local PostgreSQL test environment", why: "Stores incident lifecycle records.", tech: "PostgreSQL, Docker Engine", impl: "docker run --name pg-test -e POSTGRES_PASSWORD=secret -d -p 5432:5432 postgres:15", outcome: "Relational database server container runs in the background.", checkpoint: "Database client successfully establishes port connection." }
        ]
    },
    {
        id: "fg-p3",
        num: 3,
        category: "cat-a",
        title: "Phase 3 — Docker",
        description: "Package API microservices into Dockerfiles and test bridge networking.",
        tasks: [
            { id: "fg-3-1", title: "Write multi-stage Dockerfiles", why: "Prepares isolated container packages.", tech: "Docker instructions, python-slim", impl: "Create Dockerfile for each microservice with pip requirements mappings.", outcome: "Declarative Docker configurations written.", checkpoint: "docker build -t local/payment-service:v1.0 succeeds." },
            { id: "fg-3-2", title: "Orchestrate environment via Docker network", why: "Enables DNS discovery outside K8s namespaces.", tech: "Docker Network CLI", impl: "docker network create SRE-network && docker run --network SRE-network", outcome: "Containers resolve each other's bridge hostnames.", checkpoint: "ping check passes between stubs." }
        ]
    },
    {
        id: "fg-p4",
        num: 4,
        category: "cat-a",
        title: "Phase 4 — Kubernetes",
        description: "Deploy microservices onto local cluster and set up health probes.",
        tasks: [
            { id: "fg-4-1", title: "Load Docker images into Kind", why: "Prevents Kind from seeking external registries.", tech: "Kind load command", impl: "kind load docker-image payment-service:v1.0 --name devops-lab", outcome: "Docker image cached in local cluster node registry.", checkpoint: "Image shows up in Kind cache logs." },
            { id: "fg-4-2", title: "Create namespace, deployments, and services", why: "Triggers K8s scheduling loops.", tech: "Kubectl YAML manifests", impl: "kubectl apply -f kubernetes/namespace.yaml -f kubernetes/payment-deployment.yaml", outcome: "Target pods deployed inside production namespace.", checkpoint: "kubectl get pods -n production returns status Running." },
            { id: "fg-4-3", title: "Configure liveness and readiness probes", why: "Allows K8s to automatically recycle dead container nodes.", tech: "HTTP health checks", impl: "Add readinessProbe and livenessProbe fields pointing to /health in deployment YAML.", outcome: "Probes active.", checkpoint: "kubectl describe deployment payment-service matches check thresholds." }
        ]
    },
    {
        id: "fg-p5",
        num: 5,
        category: "cat-a",
        title: "Phase 5 — Monitoring",
        description: "Deploy Prometheus metric scrapers and setup Grafana alerts.",
        tasks: [
            { id: "fg-5-1", title: "Install Kube-Prometheus stack via Helm", why: "Prepares metrics storage and Grafana configurations.", tech: "Helm Charts, Prometheus stack", impl: "helm install monitor prometheus-community/kube-prometheus-stack -n monitoring", outcome: "Telemetry scrapers running in monitoring namespace.", checkpoint: "Accessing port 3000 displays Grafana login interface." },
            { id: "fg-5-2", title: "Map Prometheus ServiceMonitor scrapes", why: "Points monitoring pipelines to microservice /metrics paths.", tech: "ServiceMonitor custom resource", impl: "kubectl apply -f kubernetes/servicemonitor.yaml matching payment labels.", outcome: "Target endpoints mapped.", checkpoint: "Prometheus targets tab lists payment-service endpoint status as UP." }
        ]
    },
    {
        id: "fg-p6",
        num: 6,
        category: "cat-a",
        title: "Phase 6 — Logging",
        description: "Centralize container logs and build a python parser.",
        tasks: [
            { id: "fg-6-1", title: "Extract container logs via shell pipeline", why: "Provides log dumps to construct parsers.", tech: "Kubectl logs", impl: "kubectl logs -n production -l app=payment-service > raw_logs.txt", outcome: "Raw access and warning log logs saved as file targets.", checkpoint: "raw_logs.txt has valid SRE output columns." },
            { id: "fg-6-2", title: "Build Python regular expression parser", why: "Converts logs to queryable structured dictionaries.", tech: "Python re module", impl: "Write parse_log_line regex pattern in src/backend/app/services/log_parser.py", outcome: "Logs converted to JSON fields.", checkpoint: "Passing access string returns parsed service name and levels." }
        ]
    },
    {
        id: "fg-p7",
        num: 7,
        category: "cat-b",
        title: "Phase 7 — ML Anomaly Detection",
        description: "Parse the BGL dataset, extract log features, and train Isolation Forest.",
        tasks: [
            { id: "fg-7-1", title: "Preprocess BGL dataset logs", why: "Establishes a baseline data pool for anomaly modeling.", tech: "Pandas library", impl: "Download and parse BGL_200k.log, dividing categories into error flags.", outcome: "CSV file output formatted.", checkpoint: "Pandas successfully counts normal vs outlier rows." },
            { id: "fg-7-2", title: "Train Isolation Forest Model", why: "Isolates and scores system anomalies.", tech: "scikit-learn IsolationForest", impl: "Fit model on numeric window vectors. Export weights using joblib.", outcome: "Weights file pkl compiled.", checkpoint: "model.predict(X_test) successfully flags anomalous outliers." }
        ]
    },
    {
        id: "fg-p8",
        num: 8,
        category: "cat-b",
        title: "Phase 8 — Incident Management Backend",
        description: "Model SQL schemas and code FastAPI CRUD control endpoints.",
        tasks: [
            { id: "fg-8-1", title: "Define SQLAlchemy schemas & Alembic migrations", why: "Sets up relational storage for incident histories.", tech: "SQLAlchemy, Alembic, PostgreSQL", impl: "Create Incident, Action, and AuditLog schemas in models. Run migrations.", outcome: "DB schemas successfully created.", checkpoint: "Tables display in PostgreSQL query tool." },
            { id: "fg-8-2", title: "Code REST backend endpoint paths", why: "Exposes control pathways to React Dashboard and AI Agent.", tech: "FastAPI router", impl: "Write routers for /api/v1/incidents/ and /api/v1/actions/.", outcome: "REST APIs active.", checkpoint: "HTTP GET request returns valid JSON payloads." }
        ]
    },
    {
        id: "fg-p9",
        num: 9,
        category: "cat-b",
        title: "Phase 9 — RAG Knowledge Base",
        description: "Embed runbook documents and index into FAISS database.",
        tasks: [
            { id: "fg-9-1", title: "Create SRE runbook troubleshooting templates", why: "Supplies system guides context to LLMs.", tech: "Markdown guides", impl: "Write markdown logs detailing database timeout and out-of-memory fixes.", outcome: "Guides cataloged.", checkpoint: "Files saved to src/rag/data/ directory." },
            { id: "fg-9-2", title: "Embed runbooks into FAISS index database", why: "Enables semantic searches on error symptoms.", tech: "FAISS, HuggingFaceEmbeddings", impl: "Chunk markdown guides and build FAISS index files in indexer.py.", outcome: "FAISS vector database stored locally.", checkpoint: "FAISS index.faiss generated in directory." }
        ]
    },
    {
        id: "fg-p10",
        num: 10,
        category: "cat-b",
        title: "Phase 10 — LLM Integration",
        description: "Configure ChatOpenAI endpoints and structure JSON inputs.",
        tasks: [
            { id: "fg-10-1", title: "Design LLM Prompt templates with RAG injection", why: "Injects logs and guides context to prevent AI hallucinations.", tech: "LangChain PromptTemplate", impl: "Write prompts feeding logs, metrics, runbooks, and anomaly scores.", outcome: "Structured diagnostic prompt created.", checkpoint: "Formatted prompt prints context correctly." },
            { id: "fg-10-2", title: "Structure output JSON via Pydantic model", why: "Guarantees output parseability by downstream controllers.", tech: "Pydantic validation schema", impl: "Code SREDiagnosis class specifying root_cause and action_type parameters.", outcome: "Validation model configured.", checkpoint: "Mock LLM output parses successfully." }
        ]
    },
    {
        id: "fg-p11",
        num: 11,
        category: "cat-c",
        title: "Phase 11 — Agentic AI",
        description: "Construct LangGraph state machine loops and define execution tools.",
        tasks: [
            { id: "fg-11-1", title: "Expose Kubernetes client python SDK tools", why: "Allows the agent to fetch logs and inspect pod statuses.", tech: "Python K8s SDK", impl: "Code get_pod_status, get_logs, and restart_service tool modules.", outcome: "Python tool helpers operational.", checkpoint: "Calling get_pod_status() returns target namespace statuses." },
            { id: "fg-11-2", title: "Map StateGraph nodes & conditional edges", why: "Governs the cognitive loops.", tech: "LangGraph StateGraph", impl: "Map scraper, diagnose, execute, and verify nodes in graph.py.", outcome: "Agent state machine compiled.", checkpoint: "Mock invocation triggers nodes sequentially." }
        ]
    },
    {
        id: "fg-p12",
        num: 12,
        category: "cat-c",
        title: "Phase 12 — Self-Healing",
        description: "Implement the closed-loop recovery sequence and safety checks.",
        tasks: [
            { id: "fg-12-1", title: "Enforce safety policies and parameter validation", why: "Prevents code injections or namespace deletions.", tech: "Python validators", impl: "Write validate_agent_action allowlist filtering target namespaces.", outcome: "Safety validation layer active.", checkpoint: "Dangerous actions return validation errors." },
            { id: "fg-12-2", title: "Build metrics verification recovery check", why: "Confirms if applied fixes recovered system health.", tech: "Prometheus client queries", impl: "Wait 20s, fetch target error rates, verify if metrics are resolved.", outcome: "Verification engine built.", checkpoint: "Healthy metrics resolve active incidents." }
        ]
    },
    {
        id: "fg-p13",
        num: 13,
        category: "cat-c",
        title: "Phase 13 — Failure Simulation",
        description: "Intentionally trigger memory exhaustion and connection pools errors.",
        tasks: [
            { id: "fg-13-1", title: "Simulate container OOMKilled events", why: "Validates memory warning alert pipelines.", tech: "K8s Limits, Stress scripts", impl: "Apply deployment configuration with 64Mi RAM limits and stress endpoint.", outcome: "Container pod restarts due to out-of-memory errors.", checkpoint: "kubectl get pods returns OOMKilled." },
            { id: "fg-13-2", title: "Simulate DB connection pool exhaustion", why: "Validates cascading timeout anomaly detection.", tech: "Postgres config, Stress calls", impl: "Limit PostgreSQL max connections to 5 and trigger parallel API queries.", outcome: "Microservice logs record DB pool timeout errors.", checkpoint: "API health check returns HTTP 500." }
        ]
    },
    {
        id: "fg-p14",
        num: 14,
        category: "cat-c",
        title: "Phase 14 — Frontend Dashboard",
        description: "Build the React health-panels and chat query interface.",
        tasks: [
            { id: "fg-14-1", title: "Build React metrics graphs and incident cards", why: "Visualizes active incidents and AI diagnostic outputs.", tech: "React UI components", impl: "Design components rendering metrics, anomaly scores, and resolution steps.", outcome: "Visual dashboard rendered.", checkpoint: "UI fetches and displays current incident records." },
            { id: "fg-14-2", title: "Code NLP Chat Assistant widget", why: "Enables operators to ask SRE diagnostics queries.", tech: "React, FastAPI gateway", impl: "Add ChatInterface mapping user text queries to LLM prompt wrappers.", outcome: "Chat widget active.", checkpoint: "Queries return detailed system explanations." }
        ]
    },
    {
        id: "fg-p15",
        num: 15,
        category: "cat-c",
        title: "Phase 15 — CI/CD",
        description: "Create GitHub actions workflows for K8s deployments.",
        tasks: [
            { id: "fg-15-1", title: "Configure deploy workflow pipeline", why: "Automates container build and namespace deployment checks.", tech: "GitHub Actions YAML", impl: "Create deploy.yaml triggered on commits to dev/prod branches.", outcome: "Actions pipeline configured.", checkpoint: "Workflow file passes syntactical checks." }
        ]
    },
    {
        id: "fg-p16",
        num: 16,
        category: "cat-c",
        title: "Phase 16 — Security Guardrails",
        description: "Enforce manual approval workflows for high-risk operations.",
        tasks: [
            { id: "fg-16-1", title: "Implement Human-in-the-loop approvals", why: "Prevents AI hallucinations from rolling back services without approval.", tech: "Status flags, React UI buttons", impl: "Configure action state to PENDING_APPROVAL if risk parameters are high.", outcome: "Risky actions paused for confirmation.", checkpoint: "High-risk actions require human click authorization." }
        ]
    },
    {
        id: "fg-p17",
        num: 17,
        category: "cat-c",
        title: "Phase 17 — Testing Suite",
        description: "Write integration tests validating the self-healing pipeline.",
        tasks: [
            { id: "fg-17-1", title: "Create PyTest recovery tests", why: "Confirms system integrity and recovery logic.", tech: "pytest, mock objects", impl: "Write test_recovery.py asserting success states after incident triggers.", outcome: "Test suites written.", checkpoint: "pytest terminal run passes all tests." }
        ]
    },
    {
        id: "fg-p18",
        num: 18,
        category: "cat-c",
        title: "Phase 18 — Production Optimization",
        description: "Configure Redis caching for logs and Celery background queues.",
        tasks: [
            { id: "fg-18-1", title: "Initialize Redis cache and background queue workers", why: "Saves DB operations and decouples background SRE runs.", tech: "Redis, Celery, Python", impl: "Deploy Redis, configure cached endpoints, and offload tasks to Celery.", outcome: "Background workers active.", checkpoint: "Tasks are processed asynchronously by Celery workers." }
        ]
    },
    {
        id: "fg-p19",
        num: 19,
        category: "cat-c",
        title: "Phase 19 — Cloud Deployment",
        description: "Provision AWS GKE resource pools and migrate configurations.",
        tasks: [
            { id: "fg-19-1", title: "Deploy cluster configurations to AWS GKE", why: "Tests the application in production cloud environments.", tech: "AWS EKS, Terraform", impl: "Configure infrastructure configurations and run deployment manifests.", outcome: "Cloud cluster online.", checkpoint: "Public cluster path returns successful health responses." }
        ]
    },
    {
        id: "fg-p20",
        num: 20,
        category: "cat-c",
        title: "Phase 20 — Final Handover Specs",
        description: "Compile system diagrams and database ER configurations.",
        tasks: [
            { id: "fg-20-1", title: "Compile complete system handover documentation", why: "Ensures codebase is easy to maintain.", tech: "Markdown, ER Diagrams", impl: "Write API specs, ER diagrams, and setup instructions in README.md.", outcome: "Handover files written.", checkpoint: "Codebase is documented and complete." }
        ]
    }
];

// 4. Component Details Mapping (same as v4)
const componentDetails = {
    developer: {
        title: "Developer Interface",
        category: "Human Operator Interface",
        desc: "The entry point for developers and SREs to ask natural language questions (e.g. 'Why is API down?' or 'Why is payment service slow?'). It acts as the conversational bridge between humans and the autonomous agent.",
        input: "User text prompt / query",
        output: "Backend agent invocation response with diagnostic evidence & actions",
        files: ["src/dashboard/components/ChatInterface.jsx", "src/backend/app/api/agent.py"]
    },
    dashboard: {
        title: "React SRE Dashboard",
        category: "User Interface",
        desc: "A rich visual web portal that displays the live status of all Kubernetes microservices, lists anomaly logs, highlights active incidents, showing diagnostic visual graphs of active LangGraph agent chains.",
        input: "REST API feeds from FastAPI backend (incidents, audit trails, metrics, logs)",
        output: "Rendered charts, interactive terminal view, approval buttons for actions",
        files: ["src/dashboard/src/App.jsx", "src/dashboard/src/components/MetricCharts.jsx"]
    },
    backend: {
        title: "FastAPI OOP Backend",
        category: "System Backend",
        desc: "The centralized hub managing application state. Structured strictly around OOP principles, it maps monitoring pipelines to Prometheus, acts as the API gateway, and hosts persistent storage handles for incidents, actions, and audit trails.",
        input: "HTTP API requests, webhooks from alerts, system telemetry feeds",
        output: "JSON responses, database updates, background tasks dispatching to the Agent",
        files: ["src/backend/app/main.py", "src/backend/app/services/kubernetes_service.py", "src/backend/app/models/incident.py"]
    },
    agent: {
        title: "LangGraph SRE Agent",
        category: "Cognitive AI Layer",
        desc: "The cognitive controller coordinating the observe-analyze-act loop. Built using LangGraph, it models troubleshooting logic as an cyclic graph of state nodes, allowing backtracking and tools invoking.",
        input: "Incident context, logs, telemetry state variables",
        output: "Next action decision path (e.g. inspect metrics, retrieve runbooks, execute tool)",
        files: ["src/backend/app/agents/devops_agent.py", "src/backend/app/agents/planner.py"]
    },
    ml: {
        title: "ML Anomaly Detector",
        category: "Traditional ML Brain",
        desc: "A scikit-learn model trained on structural log features. It monitors log frequencies and metric combinations, evaluating logs through Isolation Forest pipelines to signal anomalies before simple threshold rules trigger.",
        input: "Structured raw logs window data, request metrics",
        output: "Anomaly flag (True/False), Isolation Forest contamination outlier score",
        files: ["src/backend/app/ml/anomaly_detector.py", "src/backend/app/ml/predictor.py"]
    },
    rag: {
        title: "RAG Runbook DB",
        category: "Knowledge Base Brain",
        desc: "A FAISS or Chroma vector database loaded with tokenized official manuals, Kubernetes debugging guidelines, and historic troubleshooting logs. It extracts semantic contexts matching active incident descriptions.",
        input: "Log error snippets, incident status descriptions",
        output: "Top 3 relevant troubleshooting runbook chunks",
        files: ["src/backend/app/services/rag_service.py", "src/backend/app/ml/vector_db.py"]
    },
    llm: {
        title: "LLM Diagnostic Reasoner",
        category: "Cognitive AI Brain",
        desc: "Generative LLM (Llama or GPT) that performs logical analysis. Provided with metrics, error logs, and RAG contextual documents, it creates an incident root cause hypothesis and coordinates repair recommendations.",
        input: "Structured prompts containing Logs + Metrics + RAG guidelines + Deployments",
        output: "Root cause diagnostics JSON (Evidence, Diagnosis, Confidence, Safe Action recommendation)",
        files: ["src/backend/app/services/llm_service.py"]
    },
    rca: {
        title: "Root Cause Analyzer",
        category: "Correlation Engine",
        desc: "The validation layer combining signals from all diagnostic brains. It correlates timing offsets (e.g. anomaly started 15 seconds after payment-service deployment) with LLM diagnostic confidence levels.",
        input: "ML anomaly flags + LLM diagnostics + Git deployment timelines",
        output: "Correlated Incident Report outlining probability metrics",
        files: ["src/backend/app/services/incident_service.py"]
    },
    policy: {
        title: "Policy Validator",
        category: "Security & Guardrails",
        desc: "A security layer that checks agent action requests. It applies security rules to verify permissions and prevent execution of arbitrary commands, protecting the cluster from model command-injection attacks.",
        input: "Proposed action payload (e.g. restart service, delete deployment)",
        output: "Validation Verdict (Approved / Blocked / Requires Human Verification)",
        files: ["src/backend/app/services/policy_service.py"]
    },
    executor: {
        title: "Tool Executor",
        category: "Cluster Operations Interface",
        desc: "The module mapping abstract action directives to physical cluster APIs. It converts safe, approved instructions (e.g. 'restart payment-service') into actual API requests invoking the Kubernetes client.",
        input: "Validated action request details",
        output: "Successful API return codes, shell outputs, or error states",
        files: ["src/backend/app/agents/executor.py", "src/backend/app/services/kubernetes_service.py"]
    },
    kubernetes: {
        title: "Kubernetes Local Cluster",
        category: "Infrastructure Environment",
        desc: "The runtime host running Docker microservices. It aggregates standard log files, outputs telemetry data streams to Prometheus scrapers, and manages service replica controllers in our lab namespace.",
        input: "Docker images, replica control requests, YAML configurations",
        output: "Live application logs, Prometheus metrics exporter, cluster event logs",
        files: ["src/kubernetes/manifests/deployment.yaml", "src/kubernetes/manifests/postgres.yaml"]
    }
};

// 5. Agent Blueprint Node Specs (same as v4)
const agentBlueprintSpecs = {
    entry: {
        title: "Incident Entry Node",
        category: "Initialization",
        desc: "This node initiates the LangGraph state machine execution. It receives incident parameters (service name, incident ID, timestamp) from Alertmanager alerts and sets the initial state schema values.",
        filename: "state.py",
        code: `from typing import TypedDict, List, Dict, Any\n\n# The shared state schema passed between nodes\nclass SREAgentState(TypedDict):\n    incident_id: str\n    service_name: str\n    logs: List[str]\n    metrics: Dict[str, Any]\n    runbooks: List[str]\n    diagnosis: str\n    plan: List[Dict[str, Any]]\n    status: str\n    iterations: int\n\n# Node function: initializes state context\ndef initialize_incident_node(state: SREAgentState) -> Dict[str, Any]:\n    print(f"Initializing SRE Agent tracking loop for Alert: {state['incident_id']}")\n    return {\n        "status": "INVESTIGATING",\n        "iterations": 0,\n        "logs": [],\n        "runbooks": []\n    }`
    },
    scraper: {
        title: "Telemetry Scraper Node",
        category: "Observability Tools",
        desc: "Calls Kubernetes and Prometheus SDK tools to gather pod statuses, restart records, events, and raw logs surrounding the service outage timestamp.",
        filename: "scraper.py",
        code: `from kubernetes import client, config\n\ndef scrape_telemetry_node(state: SREAgentState) -> Dict[str, Any]:\n    service = state["service_name"]\n    config.load_incluster_config()\n    v1 = client.CoreV1Api()\n    \n    # 1. Fetch Pod statuses in namespace\n    pods = v1.list_namespaced_pod("production", label_selector=f"app={service}")\n    \n    # 2. Extract logs\n    logs_extracted = []\n    for pod in pods.items:\n        logs = v1.read_namespaced_pod_log(\n            name=pod.metadata.name,\n            namespace="production",\n            tail_lines=50\n        )\n        logs_extracted.append(logs)\n        \n    # 3. Simulate metrics map output\n    return {\n        "logs": logs_extracted,\n        "metrics": {"cpu": "94%", "error_rate": "28%"}\n    }`
    },
    rag_search: {
        title: "RAG Query Node",
        category: "Knowledge Search",
        desc: "Vectorizes log traces using embeddings and searches the vector store index (FAISS or Chroma DB) for matching runbooks and historic resolution guides.",
        filename: "rag_service.py",
        code: `from langchain_community.vectorstores import FAISS\nfrom langchain_openai import OpenAIEmbeddings\n\ndef query_knowledge_base_node(state: SREAgentState) -> Dict[str, Any]:\n    # Combine logs as search query\n    search_query = "\\n".join(state["logs"][:2])\n    \n    # Load vectors index\n    db = FAISS.load_local("runbooks_vector_db", OpenAIEmbeddings())\n    docs = db.similarity_search(search_query, k=2)\n    \n    runbook_contents = [doc.page_content for doc in docs]\n    return {\n        "runbooks": runbook_contents\n    }`
    },
    llm_diagnose: {
        title: "LLM Diagnostic Reasoner Node",
        category: "GenAI Diagnostics",
        desc: "Assembles current metrics, logs, and runbooks into a prompt context, calling Llama/GPT to output structured RCA diagnostics and recommended repair actions.",
        filename: "diagnose.py",
        code: `from langchain_core.prompts import PromptTemplate\nfrom langchain_openai import ChatOpenAI\n\ndef llm_diagnostics_node(state: SREAgentState) -> Dict[str, Any]:\n    prompt = PromptTemplate.from_template(\n        "You are an SRE. Given logs: {logs}\\nMetrics: {metrics}\\nRunbook: {runbooks}\\n"\n        "Analyze and return JSON matching: {\\n  'root_cause': str,\\n  'action': str,\\n  'confidence': float\\n}"\n    )\n    llm = ChatOpenAI(model="gpt-4o", temperature=0)\n    chain = prompt | llm.with_structured_output(IncidentReport)\n    report = chain.invoke({\n        "logs": state["logs"],\n        "metrics": state["metrics"],\n        "runbooks": state["runbooks"]\n    })\n    return {\n        "diagnosis": report.root_cause,\n        "plan": [{"type": report.action, "confidence": report.confidence}]\n    }`
    },
    policy_gate: {
        title: "Policy Validator Node",
        category: "Guardrails & Security",
        desc: "Validates the LLM's recommended repair actions against a static allowlist and verification rules before forwarding details to the Tool Executor.",
        filename: "policy.py",
        code: `def policy_validator_node(state: SREAgentState) -> Dict[str, Any]:\n    action = state["plan"][0]\n    # Allowed safe list\n    SAFE_ACTIONS = ["restart_pod", "rollback_deployment", "scale_replicas"]\n    \n    if action["type"] not in SAFE_ACTIONS:\n        print(f"CRITICAL: Proposed action '{action['type']}' blocked by policy.")\n        return {"status": "BLOCKED"}\n        \n    if action["confidence"] < 0.80:\n        print("Warning: Action confidence too low. Escalating for manual approval.")\n        return {"status": "REQUIRES_APPROVAL"}\n        \n    return {"status": "APPROVED"}`
    },
    action_exec: {
        title: "Tool Executor Node",
        category: "Cluster Actions",
        desc: "Executes the approved recovery operation (e.g., triggering rolling restarts, undoing deployments, scaling replica pods) via the Kubernetes client.",
        filename: "executor.py",
        code: `from kubernetes import client\n\ndef execute_recovery_node(state: SREAgentState) -> Dict[str, Any]:\n    if state["status"] != "APPROVED":\n        print("Skipping execution: Action not approved.")\n        return {"action_result": "UNAUTHORIZED"}\n        \n    action = state["plan"][0]\n    service = state["service_name"]\n    apps_v1 = client.AppsV1Api()\n    \n    if action["type"] == "restart_pod":\n        # Patch deployment metadata to trigger rolling update restart\n        apps_v1.patch_namespaced_deployment(\n            name=service, namespace="production",\n            body={"spec": {"template": {"metadata": {"annotations": {"restartedAt": datetime.now().isoformat()}}}}}\n        )\n    return {"action_result": "SUCCESS"}`
    },
    verifier: {
        title: "Verification Loop Node",
        category: "SRE Controller Feedback",
        desc: "Polls service latency and error rates. Routes the graph state to resolve if healthy, or increments iterations to re-attempt diagnostics up to a maximum limit.",
        filename: "verifier.py",
        code: `def verify_system_health_node(state: SREAgentState) -> Dict[str, Any]:\n    # Query metric API\n    error_rate = fetch_current_error_rate(state["service_name"])\n    \n    if error_rate < 0.01:\n        print("System fully recovered.")\n        return {"status": "RESOLVED"}\n        \n    if state["iterations"] >= 3:\n        print("Action ineffective. Escalating to human SRE.")\n        return {"status": "FAILED"}\n        \n    # Route graph back to Telemetry Scraper\n    return {\n        "iterations": state["iterations"] + 1,\n        "status": "RETRY"\n    }`
    }
};

// Agent Blueprint Sub-checklist tasks
const agentChecklistTasks = [
    { id: "agt-1", text: "Define SREAgentState fields (TypedDict schema in state.py)", outcome: "Shared dictionary maintaining logs, metrics, plan, status, and iteration count." },
    { id: "agt-2", text: "Implement K8s Client scraper utility (CoreV1 API and AppsV1 API helper scripts)", outcome: "Python modules that load configs and return pod logs and metrics." },
    { id: "agt-3", text: "Index SRE troubleshooting runbooks (Embed markdown files to Chroma/FAISS database)", outcome: "Indexed vector store file registry queryable by prompt contexts." },
    { id: "agt-4", text: "Configure PromptTemplate for diagnostic RCA engine", outcome: "Strict LLM prompts requesting structured JSON output." },
    { id: "agt-5", text: "Code the Policy Gatekeeper class (Allowlisting restart & scale configurations)", outcome: "Validation block returning APPROVED, BLOCKED, or REQUIRES_APPROVAL." },
    { id: "agt-6", text: "Integrate LangGraph StateGraph flow nodes & conditional edges", outcome: "A functional state-machine routing script running locally." }
];

// Global variables
let checkedTasks = {};
let currentActiveTab = "dashboard";
let currentActiveAgentNode = "entry";

// Initialize DOM
document.addEventListener("DOMContentLoaded", () => {
    loadStateFromStorage();
    initNavigation();
    renderChecklists();
    renderAgentChecklist();
    renderSetupTimeline();
    renderFlowGuide();
    renderDashboardCards();
    updateAllProgress();
    initArchitectureDetailExplorer();
    initAgentBlueprintViewer();
});

// Navigation
function initNavigation() {
    const navButtons = document.querySelectorAll(".sidebar-nav .nav-btn");
    const contentPanels = document.querySelectorAll(".content-panel");
    const tabTitle = document.getElementById("current-tab-title");
    const tabSubtitle = document.getElementById("current-tab-subtitle");

    const headerDetails = {
        dashboard: { title: "Dashboard Overview", subtitle: "Real-time status of your learning journey & system architecture." },
        "flow-guide": { title: "Complete Step-by-Step Implementation Checklist", subtitle: "Chronological master checklist covering all 21 phases." },
        "setup-guide": { title: "Chronological Setup Guide", subtitle: "Sequential implementation steps resolving database and service dependencies first." },
        architecture: { title: "System Architecture", subtitle: "Inspect the 5 brains and data flows of the SRE Agent." },
        "agent-blueprint": { title: "Agent Implementation Blueprint", subtitle: "Detailed state nodes, configurations, and LangGraph blueprints." },
        checklists: { title: "Learning Roadmap & Checklists", subtitle: "Interactive implementation checklist for all 10 project phases." },
        resources: { title: "Resources & Cheat Sheets", subtitle: "Access manuals, command shortcuts, and reference implementations." }
    };

    navButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const tabId = btn.getAttribute("data-tab");
            currentActiveTab = tabId;

            navButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            contentPanels.forEach(panel => {
                panel.classList.remove("active");
                if (panel.id === `tab-${tabId}`) {
                    panel.classList.add("active");
                }
            });

            if (headerDetails[tabId]) {
                tabTitle.textContent = headerDetails[tabId].title;
                tabSubtitle.textContent = headerDetails[tabId].subtitle;
            }
        });
    });
}

// Storage
function loadStateFromStorage() {
    const saved = localStorage.getItem("autosre_tasks_state");
    if (saved) {
        try { checkedTasks = JSON.parse(saved); } catch (e) { checkedTasks = {}; }
    } else {
        checkedTasks = {};
    }
}

function saveStateToStorage() {
    localStorage.setItem("autosre_tasks_state", JSON.stringify(checkedTasks));
}

// Progress Calculations
function updateAllProgress() {
    let totalTasks = 0;
    let completedTasks = 0;

    const catCounts = {
        "cat-a": { total: 0, completed: 0 },
        "cat-b": { total: 0, completed: 0 },
        "cat-c": { total: 0, completed: 0 }
    };

    // 1. Roadmap checklists
    roadmapData.forEach(phase => {
        phase.tasks.forEach(task => {
            totalTasks++;
            const isDone = !!checkedTasks[task.id];
            if (isDone) completedTasks++;

            if (catCounts[phase.category]) {
                catCounts[phase.category].total++;
                if (isDone) catCounts[phase.category].completed++;
            }
        });

        const phaseTotal = phase.tasks.length;
        const phaseCompleted = phase.tasks.filter(t => !!checkedTasks[t.id]).length;
        const phasePct = Math.round((phaseCompleted / phaseTotal) * 100);

        const badgeMini = document.getElementById(`phase-progress-${phase.id}`);
        if (badgeMini) badgeMini.textContent = `${phasePct}%`;

        const dbPhaseProgressTxt = document.getElementById(`db-phase-percent-${phase.id}`);
        const dbPhaseProgressBar = document.getElementById(`db-phase-bar-${phase.id}`);
        if (dbPhaseProgressTxt && dbPhaseProgressBar) {
            dbPhaseProgressTxt.textContent = `${phasePct}%`;
            dbPhaseProgressBar.style.width = `${phasePct}%`;
        }

        const accordionItem = document.getElementById(`accordion-${phase.id}`);
        if (accordionItem) {
            if (phasePct === 100) {
                accordionItem.classList.add("complete");
            } else {
                accordionItem.classList.remove("complete");
            }
        }
    });

    // 2. SRE Agent subchecklist
    let completedAgentTasks = 0;
    agentChecklistTasks.forEach(task => {
        totalTasks++;
        const isDone = !!checkedTasks[task.id];
        if (isDone) {
            completedTasks++;
            completedAgentTasks++;
        }
        catCounts["cat-c"].total++;
        if (isDone) catCounts["cat-c"].completed++;
    });

    // 3. Chronological setup guide
    setupTimelineSteps.forEach(step => {
        totalTasks++;
        const isDone = !!checkedTasks[step.id];
        if (isDone) completedTasks++;

        if (step.num <= 3) {
            catCounts["cat-a"].total++;
            if (isDone) catCounts["cat-a"].completed++;
        } else if (step.num <= 9) {
            catCounts["cat-b"].total++;
            if (isDone) catCounts["cat-b"].completed++;
        } else {
            catCounts["cat-c"].total++;
            if (isDone) catCounts["cat-c"].completed++;
        }

        const stepCard = document.getElementById(`step-card-${step.id}`);
        if (stepCard) {
            if (isDone) stepCard.classList.add("checked");
            else stepCard.classList.remove("checked");
        }
    });

    // 4. Flow Guide Checklist Progress
    flowGuidePhases.forEach(phase => {
        let phaseTotal = phase.tasks.length;
        let phaseCompleted = 0;

        phase.tasks.forEach(task => {
            totalTasks++;
            const isDone = !!checkedTasks[task.id];
            if (isDone) {
                completedTasks++;
                phaseCompleted++;
            }

            if (phase.num <= 6) {
                catCounts["cat-a"].total++;
                if (isDone) catCounts["cat-a"].completed++;
            } else if (phase.num <= 10) {
                catCounts["cat-b"].total++;
                if (isDone) catCounts["cat-b"].completed++;
            } else {
                catCounts["cat-c"].total++;
                if (isDone) catCounts["cat-c"].completed++;
            }

            const itemNode = document.getElementById(`fg-item-${task.id}`);
            if (itemNode) {
                if (isDone) itemNode.classList.add("done");
                else itemNode.classList.remove("done");
            }
        });

        const phasePct = phaseTotal > 0 ? Math.round((phaseCompleted / phaseTotal) * 100) : 0;
        const phaseProgressMini = document.getElementById(`fg-progress-${phase.id}`);
        if (phaseProgressMini) phaseProgressMini.textContent = `${phasePct}%`;

        const phaseAccordionItem = document.getElementById(`fg-accordion-${phase.id}`);
        if (phaseAccordionItem) {
            if (phasePct === 100) {
                phaseAccordionItem.classList.add("complete");
                const badge = phaseAccordionItem.querySelector(".accordion-indicator-badge");
                if (badge) badge.textContent = "Complete";
            } else {
                phaseAccordionItem.classList.remove("complete");
                const badge = phaseAccordionItem.querySelector(".accordion-indicator-badge");
                if (badge) badge.textContent = "In Progress";
            }
        }
    });

    // Global counts
    const globalPct = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;
    document.getElementById("completed-tasks-count").textContent = completedTasks;
    document.getElementById("total-tasks-count").textContent = totalTasks;
    document.getElementById("global-progress-percent").textContent = `${globalPct}%`;

    const radial = document.getElementById("global-progress-radial");
    if (radial) {
        radial.style.background = `conic-gradient(var(--purple) ${globalPct}%, var(--bg-main) ${globalPct}%)`;
    }

    for (let cat in catCounts) {
        const stats = catCounts[cat];
        const pct = stats.total > 0 ? Math.round((stats.completed / stats.total) * 100) : 0;
        const percentLabel = document.getElementById(`${cat}-percent`);
        const bar = document.getElementById(`${cat}-bar`);
        if (percentLabel) percentLabel.textContent = `${pct}%`;
        if (bar) bar.style.width = `${pct}%`;
    }

    const controlBarTxt = document.getElementById("checklist-completion-txt");
    if (controlBarTxt) {
        controlBarTxt.textContent = `${completedTasks}/${totalTasks} (${globalPct}%)`;
    }

    document.getElementById("dashboard-resolved-count").textContent = `${completedAgentTasks} / ${agentChecklistTasks.length}`;

    const anomalyTxt = document.getElementById("dashboard-anomaly-score");
    if (anomalyTxt) {
        if (globalPct > 80) {
            anomalyTxt.textContent = "Autonomous";
            anomalyTxt.style.color = "var(--green)";
        } else if (globalPct > 40) {
            anomalyTxt.textContent = "Standard API";
            anomalyTxt.style.color = "var(--blue)";
        } else {
            anomalyTxt.textContent = "Observability";
            anomalyTxt.style.color = "var(--orange)";
        }
    }
}

// Render normal Roadmap
function renderChecklists() {
    const container = document.getElementById("phases-accordion-container");
    if (!container) return;

    container.innerHTML = "";

    roadmapData.forEach((phase) => {
        const isPhaseComplete = phase.tasks.every(t => !!checkedTasks[t.id]);
        const completeClass = isPhaseComplete ? "complete" : "";
        const phaseCompletedCount = phase.tasks.filter(t => !!checkedTasks[t.id]).length;
        const phasePct = Math.round((phaseCompletedCount / phase.tasks.length) * 100);

        const accordion = document.createElement("div");
        accordion.className = `accordion-item ${completeClass}`;
        accordion.id = `accordion-${phase.id}`;
        accordion.setAttribute("data-category", phase.category);

        accordion.innerHTML = `
            <div class="accordion-header">
                <div class="accordion-title-block">
                    <div class="accordion-num">${phase.num}</div>
                    <div class="accordion-title-text">
                        <h4>${phase.title}</h4>
                        <p>${phase.description}</p>
                    </div>
                </div>
                <div class="accordion-header-right">
                    <span class="accordion-indicator-badge">${isPhaseComplete ? 'Complete' : 'In Progress'}</span>
                    <div class="accordion-progress-mini">
                        <i class="fa-solid fa-list-check"></i>
                        <span id="phase-progress-${phase.id}">${phasePct}%</span>
                    </div>
                    <i class="fa-solid fa-chevron-down accordion-chevron"></i>
                </div>
            </div>
            <div class="accordion-content">
                <div class="checklist-container">
                    <!-- tasks will populate -->
                </div>
            </div>
        `;

        const header = accordion.querySelector(".accordion-header");
        header.addEventListener("click", () => {
            accordion.classList.toggle("expanded");
        });

        const listContainer = accordion.querySelector(".checklist-container");
        phase.tasks.forEach(task => {
            const isTaskDone = !!checkedTasks[task.id];
            const doneClass = isTaskDone ? "done" : "";

            const taskItem = document.createElement("div");
            taskItem.className = `checklist-item ${doneClass}`;
            taskItem.id = `item-${task.id}`;

            taskItem.innerHTML = `
                <div class="checkbox-wrapper">
                    <input type="checkbox" class="custom-checkbox" id="chk-${task.id}" ${isTaskDone ? 'checked' : ''} />
                </div>
                <div class="checklist-item-content">
                    <div class="checklist-item-title">
                        <span>${task.title}</span>
                        <span class="task-tag">${task.tag}</span>
                    </div>
                    <p class="checklist-item-desc">${task.desc}</p>
                    ${task.code ? `
                    <div class="checklist-item-code">
                        <code>${escapeHtml(task.code)}</code>
                        <button class="copy-btn" title="Copy Command" data-code="${escapeHtml(task.code)}">
                            <i class="fa-regular fa-copy"></i>
                        </button>
                    </div>` : ''}
                    <div class="checklist-item-outcome">
                        <i class="fa-solid fa-circle-check"></i>
                        <span>Expected Outcome: ${task.outcome}</span>
                    </div>
                </div>
            `;

            const checkbox = taskItem.querySelector(".custom-checkbox");
            checkbox.addEventListener("change", (e) => {
                const checked = e.target.checked;
                checkedTasks[task.id] = checked;
                if (checked) taskItem.classList.add("done");
                else taskItem.classList.remove("done");
                saveStateToStorage();
                updateAllProgress();
            });

            const copyBtn = taskItem.querySelector(".copy-btn");
            if (copyBtn) {
                copyBtn.addEventListener("click", () => {
                    const code = copyBtn.getAttribute("data-code");
                    navigator.clipboard.writeText(code).then(() => {
                        const icon = copyBtn.querySelector("i");
                        icon.className = "fa-solid fa-check";
                        icon.style.color = "var(--green)";
                        setTimeout(() => {
                            icon.className = "fa-regular fa-copy";
                            icon.style.color = "";
                        }, 1500);
                    });
                });
            }

            listContainer.appendChild(taskItem);
        });

        container.appendChild(accordion);
    });

    const filterButtons = document.querySelectorAll(".filter-group .filter-btn");
    filterButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            filterButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            const filter = btn.getAttribute("data-filter");
            const accordionItems = container.querySelectorAll(".accordion-item");

            accordionItems.forEach(item => {
                const cat = item.getAttribute("data-category");
                if (filter === "all" || cat === filter) {
                    item.classList.remove("collapsed-item");
                } else {
                    item.classList.add("collapsed-item");
                }
            });
        });
    });
}

// Render Agent subchecklist
function renderAgentChecklist() {
    const container = document.getElementById("agent-tasks-container");
    if (!container) return;

    container.innerHTML = "";

    agentChecklistTasks.forEach(task => {
        const isTaskDone = !!checkedTasks[task.id];
        const doneClass = isTaskDone ? "done" : "";

        const taskItem = document.createElement("div");
        taskItem.className = `checklist-item ${doneClass}`;
        taskItem.id = `item-${task.id}`;
        taskItem.style.padding = "10px 14px";
        taskItem.style.gap = "10px";

        taskItem.innerHTML = `
            <div class="checkbox-wrapper">
                <input type="checkbox" class="custom-checkbox" id="chk-${task.id}" ${isTaskDone ? 'checked' : ''} />
            </div>
            <div class="checklist-item-content">
                <div class="checklist-item-title" style="font-size: 13px;">
                    <span>${task.text}</span>
                </div>
                <div class="checklist-item-outcome" style="margin-top: 2px; font-size: 11px;">
                    <i class="fa-solid fa-circle-check"></i>
                    <span>Outcome: ${task.outcome}</span>
                </div>
            </div>
        `;

        const checkbox = taskItem.querySelector(".custom-checkbox");
        checkbox.addEventListener("change", (e) => {
            const checked = e.target.checked;
            checkedTasks[task.id] = checked;
            if (checked) taskItem.classList.add("done");
            else taskItem.classList.remove("done");
            saveStateToStorage();
            updateAllProgress();
        });

        container.appendChild(taskItem);
    });
}

// Render Chronological Setup Guide
function renderSetupTimeline() {
    const container = document.getElementById("setup-timeline-container");
    if (!container) return;

    container.innerHTML = "";

    setupTimelineSteps.forEach(step => {
        const isDone = !!checkedTasks[step.id];
        const doneClass = isDone ? "checked" : "";

        const stepNode = document.createElement("div");
        stepNode.className = `timeline-step-card ${doneClass}`;
        stepNode.id = `step-card-${step.id}`;

        stepNode.innerHTML = `
            <div class="timeline-left">
                <div class="timeline-dot">${step.num}</div>
            </div>
            <div class="timeline-card">
                <div class="timeline-card-header">
                    <div class="timeline-card-title">
                        <span class="timeline-phase-tag">${step.phaseTag}</span>
                        <h4>${step.title}</h4>
                    </div>
                    <div class="checkbox-wrapper">
                        <input type="checkbox" class="custom-checkbox" id="chk-${step.id}" ${isDone ? 'checked' : ''} />
                    </div>
                </div>
                <p class="timeline-card-desc">${step.desc}</p>
                ${step.code ? `
                <div class="timeline-card-code">
                    <code>${escapeHtml(step.code)}</code>
                    <button class="copy-btn" title="Copy Command" data-code="${escapeHtml(step.code)}">
                        <i class="fa-regular fa-copy"></i>
                    </button>
                </div>` : ''}
                <div class="timeline-card-outcome">
                    <i class="fa-solid fa-circle-check"></i>
                    <span>Verification Outcome: ${step.outcome}</span>
                </div>
            </div>
        `;

        const checkbox = stepNode.querySelector(".custom-checkbox");
        checkbox.addEventListener("change", (e) => {
            const checked = e.target.checked;
            checkedTasks[step.id] = checked;
            if (checked) stepNode.classList.add("checked");
            else stepNode.classList.remove("checked");
            saveStateToStorage();
            updateAllProgress();
        });

        const copyBtn = stepNode.querySelector(".copy-btn");
        if (copyBtn) {
            copyBtn.addEventListener("click", () => {
                const code = copyBtn.getAttribute("data-code");
                navigator.clipboard.writeText(code).then(() => {
                    const icon = copyBtn.querySelector("i");
                    icon.className = "fa-solid fa-check";
                    icon.style.color = "var(--green)";
                    setTimeout(() => {
                        icon.className = "fa-regular fa-copy";
                        icon.style.color = "";
                    }, 1500);
                });
            });
        }

        container.appendChild(stepNode);
    });
}

// 14. Render Interactive Flow Guide (21 Phases)
function renderFlowGuide() {
    const container = document.getElementById("flow-guide-accordion-container");
    if (!container) return;

    container.innerHTML = "";

    flowGuidePhases.forEach(phase => {
        const totalPhaseTasks = phase.tasks.length;
        const completedPhaseTasks = phase.tasks.filter(t => !!checkedTasks[t.id]).length;
        const phasePct = totalPhaseTasks > 0 ? Math.round((completedPhaseTasks / totalPhaseTasks) * 100) : 0;

        const accordion = document.createElement("div");
        accordion.className = `accordion-item ${phasePct === 100 ? 'complete' : ''}`;
        accordion.id = `fg-accordion-${phase.id}`;
        accordion.setAttribute("data-category", phase.category);

        accordion.innerHTML = `
            <div class="accordion-header">
                <div class="accordion-title-block">
                    <div class="accordion-num">${phase.num}</div>
                    <div class="accordion-title-text">
                        <h4>${phase.title}</h4>
                        <p>${phase.description}</p>
                    </div>
                </div>
                <div class="accordion-header-right">
                    <span class="accordion-indicator-badge">${phasePct === 100 ? 'Complete' : 'In Progress'}</span>
                    <div class="accordion-progress-mini">
                        <i class="fa-solid fa-list-check"></i>
                        <span id="fg-progress-${phase.id}">${phasePct}%</span>
                    </div>
                    <i class="fa-solid fa-chevron-down accordion-chevron"></i>
                </div>
            </div>
            <div class="accordion-content">
                <div class="checklist-container" id="fg-list-${phase.id}">
                    <!-- Tasks will load here -->
                </div>
            </div>
        `;

        const header = accordion.querySelector(".accordion-header");
        header.addEventListener("click", () => {
            accordion.classList.toggle("expanded");
        });

        const listContainer = accordion.querySelector(".checklist-container");
        phase.tasks.forEach(task => {
            const isDone = !!checkedTasks[task.id];
            const doneClass = isDone ? "done" : "";

            const taskItem = document.createElement("div");
            taskItem.className = `checklist-item ${doneClass}`;
            taskItem.id = `fg-item-${task.id}`;

            taskItem.innerHTML = `
                <div class="checkbox-wrapper">
                    <input type="checkbox" class="custom-checkbox" id="chk-${task.id}" ${isDone ? 'checked' : ''} />
                </div>
                <div class="checklist-item-content">
                    <div class="checklist-item-title">
                        <span>${task.title}</span>
                    </div>
                    <p class="checklist-item-desc"><strong>Why:</strong> ${task.why}</p>
                    <p class="checklist-item-desc"><strong>Tools:</strong> ${task.tech}</p>
                    <p class="checklist-item-desc"><strong>Implementation:</strong> ${task.impl}</p>
                    <p class="checklist-item-outcome">
                        <i class="fa-solid fa-circle-info"></i>
                        <span>Expected Result: ${task.outcome}</span>
                    </p>
                    <div class="checklist-item-outcome" style="margin-top:2px;">
                        <i class="fa-solid fa-flag-checkered" style="color:var(--purple)"></i>
                        <span>Checkpoint: ${task.checkpoint}</span>
                    </div>
                </div>
            `;

            const checkbox = taskItem.querySelector(".custom-checkbox");
            checkbox.addEventListener("change", (e) => {
                const checked = e.target.checked;
                checkedTasks[task.id] = checked;
                if (checked) taskItem.classList.add("done");
                else taskItem.classList.remove("done");
                saveStateToStorage();
                updateAllProgress();
            });

            listContainer.appendChild(taskItem);
        });

        container.appendChild(accordion);
    });
}

// Render Dashboard phase summary grid cards
function renderDashboardCards() {
    const grid = document.getElementById("dashboard-phase-cards");
    if (!grid) return;

    grid.innerHTML = "";

    roadmapData.forEach(phase => {
        const phaseCompletedCount = phase.tasks.filter(t => !!checkedTasks[t.id]).length;
        const phasePct = Math.round((phaseCompletedCount / phase.tasks.length) * 100);

        const card = document.createElement("div");
        card.className = "dashboard-phase-card";
        card.innerHTML = `
            <div class="phase-card-header ${phasePct === 100 ? 'complete' : ''}">
                <span>Phase ${phase.num}</span>
                <span class="phase-status-badge">${phasePct === 100 ? 'Complete' : 'In Progress'}</span>
            </div>
            <h4>${phase.title.split(": ")[1]}</h4>
            <p>${phase.description}</p>
            <div class="phase-card-progress">
                <div class="progress-bar-container" style="flex-grow: 1;">
                    <div class="progress-bar purple-bar" id="db-phase-bar-${phase.id}" style="width: ${phasePct}%"></div>
                </div>
                <span id="db-phase-percent-${phase.id}">${phasePct}%</span>
            </div>
        `;

        card.addEventListener("click", () => {
            const roadmapNavBtn = document.getElementById("nav-checklists");
            if (roadmapNavBtn) {
                roadmapNavBtn.click();
                setTimeout(() => {
                    const accordion = document.getElementById(`accordion-${phase.id}`);
                    if (accordion) {
                        accordion.classList.add("expanded");
                        accordion.scrollIntoView({ behavior: "smooth", block: "center" });
                    }
                }, 100);
            }
        });

        grid.appendChild(card);
    });
}

// Architecture diagrams interactions
function initArchitectureDetailExplorer() {
    const nodes = document.querySelectorAll(".interactive-diagram .node");
    const detailPane = document.getElementById("architecture-details");
    const detailPanePlaceholder = document.querySelector(".architecture-info-pane .instruction-text");

    const detailTitle = document.getElementById("detail-title");
    const detailBadge = document.getElementById("detail-badge");
    const detailDesc = document.getElementById("detail-desc");
    const detailInput = document.getElementById("detail-input");
    const detailOutput = document.getElementById("detail-output");
    const detailFilesList = document.getElementById("detail-files");

    nodes.forEach(node => {
        node.addEventListener("click", () => {
            nodes.forEach(n => n.classList.remove("active"));
            node.classList.add("active");

            const nodeId = node.getAttribute("data-node");
            const data = componentDetails[nodeId];

            if (data) {
                detailPanePlaceholder.classList.add("hidden");
                detailPane.classList.remove("hidden");

                detailTitle.textContent = data.title;
                detailBadge.textContent = data.category;
                
                detailBadge.className = "badge";
                if (nodeId === "ml") detailBadge.classList.add("ml");
                if (nodeId === "rag") detailBadge.classList.add("rag");
                if (nodeId === "llm" || nodeId === "agent") detailBadge.classList.add("llm");
                if (nodeId === "kubernetes") detailBadge.classList.add("infra");

                detailDesc.textContent = data.desc;
                detailInput.textContent = data.input;
                detailOutput.textContent = data.output;

                detailFilesList.innerHTML = "";
                data.files.forEach(file => {
                    const li = document.createElement("li");
                    li.textContent = file;
                    detailFilesList.appendChild(li);
                });
            }
        });
    });
}

// Agent blueprint nodes interactions
function initAgentBlueprintViewer() {
    const nodes = document.querySelectorAll(".agent-flow-graph .graph-node");
    
    const specTitle = document.getElementById("agent-spec-title");
    const specBadge = document.getElementById("agent-spec-badge");
    const specDesc = document.getElementById("agent-spec-desc");
    const specCode = document.getElementById("agent-spec-code");
    const codeFilename = document.getElementById("agent-code-filename");
    const copyBtn = document.getElementById("agent-spec-copy-btn");

    nodes.forEach(node => {
        node.addEventListener("click", () => {
            nodes.forEach(n => n.classList.remove("active"));
            node.classList.add("active");

            currentActiveAgentNode = node.getAttribute("data-agent-node");
            const spec = agentBlueprintSpecs[currentActiveAgentNode];

            if (spec) {
                specTitle.textContent = spec.title;
                specBadge.textContent = spec.category;
                specDesc.textContent = spec.desc;
                codeFilename.textContent = spec.filename;
                specCode.textContent = spec.code;
            }
        });
    });

    if (copyBtn) {
        copyBtn.addEventListener("click", () => {
            const specText = specCode.textContent;
            navigator.clipboard.writeText(specText).then(() => {
                const icon = copyBtn.querySelector("i");
                icon.className = "fa-solid fa-check";
                icon.style.color = "var(--green)";
                setTimeout(() => {
                    icon.className = "fa-regular fa-copy";
                    icon.style.color = "";
                }, 1500);
            });
        });
    }

    const defaultNode = document.querySelector(".agent-flow-graph .graph-node[data-agent-node='entry']");
    if (defaultNode) defaultNode.click();
}

// HTML escape helper
function escapeHtml(str) {
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
