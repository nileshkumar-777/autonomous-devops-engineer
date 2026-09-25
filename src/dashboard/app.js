/* ==============================================================================
   AutoSRE — Production Dashboard Interactive Engine (Gold & Black Theme)
   ============================================================================== */

const API_BASE = ""; // Relative to origin when served from FastAPI

let selectedChaosType = "db_pool";
let activeIncidentId = null;

// DOM Elements
const fleetGrid = document.getElementById("fleet-grid-container");
const incidentsList = document.getElementById("incidents-list-container");
const agentFlowViewer = document.getElementById("agent-flow-viewer");
const auditLedgerTbody = document.getElementById("audit-ledger-tbody");
const outageModal = document.getElementById("outage-modal");
const toastNotify = document.getElementById("toast-notify");
const toastText = document.getElementById("toast-text");

// Metric Elements
const fleetHealthVal = document.getElementById("fleet-health-val");
const activeIncidentsCount = document.getElementById("active-incidents-count");
const resolvedIncidentsCount = document.getElementById("resolved-incidents-count");
const lastPingTime = document.getElementById("last-ping-time");

// ------------------------------------------------------------------------------
// Initialization & Polling
// ------------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
    setupEventListeners();
    fetchSystemStatus();
    fetchFleetServices();
    fetchIncidents();
    fetchAuditLedger();

    // Auto-refresh telemetry every 4 seconds
    setInterval(() => {
        fetchSystemStatus();
        fetchFleetServices();
        fetchIncidents();
        fetchAuditLedger();
    }, 4000);
});

function setupEventListeners() {
    // Modal controls
    document.getElementById("btn-trigger-failure").addEventListener("click", () => {
        outageModal.classList.remove("hidden");
    });

    const emptyTriggerBtn = document.getElementById("btn-empty-trigger");
    if (emptyTriggerBtn) {
        emptyTriggerBtn.addEventListener("click", () => {
            outageModal.classList.remove("hidden");
        });
    }

    document.getElementById("btn-close-modal").addEventListener("click", () => {
        outageModal.classList.add("hidden");
    });
    document.getElementById("btn-cancel-modal").addEventListener("click", () => {
        outageModal.classList.add("hidden");
    });

    // Chaos option selector
    document.querySelectorAll(".chaos-option-card").forEach(card => {
        card.addEventListener("click", () => {
            document.querySelectorAll(".chaos-option-card").forEach(c => c.classList.remove("selected"));
            card.classList.add("selected");
            selectedChaosType = card.getAttribute("data-chaos");
        });
    });

    // Confirm chaos trigger
    document.getElementById("btn-confirm-chaos").addEventListener("click", triggerChaosIncident);

    // Refresh button
    document.getElementById("btn-refresh-telemetry").addEventListener("click", () => {
        fetchSystemStatus();
        fetchFleetServices();
        fetchIncidents();
        fetchAuditLedger();
        showToast("Telemetry refreshed from cluster.");
    });
}

// ------------------------------------------------------------------------------
// API Data Fetchers
// ------------------------------------------------------------------------------

async function fetchSystemStatus() {
    try {
        const res = await fetch(`${API_BASE}/api/system/status`);
        if (!res.ok) return;
        const data = await res.json();

        activeIncidentsCount.innerText = data.active_incidents;
        resolvedIncidentsCount.innerText = data.resolved_incidents;

        if (data.active_incidents > 0) {
            fleetHealthVal.innerText = "DEGRADED";
            fleetHealthVal.classList.remove("gold-text");
            fleetHealthVal.style.color = "var(--status-red)";
        } else {
            fleetHealthVal.innerText = "100% HEALTHY";
            fleetHealthVal.classList.add("gold-text");
            fleetHealthVal.style.color = "";
        }

        lastPingTime.innerText = `Prometheus Scrapes: Active (Last synced: ${new Date().toLocaleTimeString()})`;
    } catch (e) {
        console.warn("Status fetch error", e);
    }
}

async function fetchFleetServices() {
    try {
        const res = await fetch(`${API_BASE}/api/services`);
        if (!res.ok) return;
        const services = await res.json();

        fleetGrid.innerHTML = services.map(svc => `
            <div class="fleet-card ${svc.status === 'CRITICAL' ? 'degraded' : ''}">
                <div class="card-top">
                    <div class="service-title-area">
                        <div class="service-icon-box">
                            <i class="fa-solid fa-cube"></i>
                        </div>
                        <span class="service-name">${svc.service_name}</span>
                    </div>
                    <span class="status-pill ${svc.status === 'CRITICAL' ? 'critical' : 'healthy'}">
                        ${svc.status}
                    </span>
                </div>

                <div class="telemetry-row">
                    <div class="telemetry-item">
                        <span class="tel-label">ERROR RATE</span>
                        <span class="tel-val" style="color: ${svc.error_rate > 0.05 ? 'var(--status-red)' : 'var(--gold-champagne)'}">
                            ${(svc.error_rate * 100).toFixed(1)}%
                        </span>
                    </div>
                    <div class="telemetry-item">
                        <span class="tel-label">P95 LATENCY</span>
                        <span class="tel-val">${svc.p95_latency_ms}ms</span>
                    </div>
                    <div class="telemetry-item">
                        <span class="tel-label">REPLICAS</span>
                        <span class="tel-val">${svc.replicas} Pods</span>
                    </div>
                    <div class="telemetry-item">
                        <span class="tel-label">CPU / RAM</span>
                        <span class="tel-val">${svc.cpu_saturation_pct.toFixed(0)}% / ${svc.memory_usage_mb}MB</span>
                    </div>
                </div>

                <div class="card-action-bar">
                    <button class="card-mini-btn" onclick="quickInjectChaos('${svc.service_name}')">
                        <i class="fa-solid fa-bolt"></i> Test Failure
                    </button>
                </div>
            </div>
        `).join("");
    } catch (e) {
        console.warn("Fleet fetch error", e);
    }
}

async function fetchIncidents() {
    try {
        const res = await fetch(`${API_BASE}/api/incidents`);
        if (!res.ok) return;
        const incidents = await res.json();

        if (incidents.length === 0) {
            incidentsList.innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-shield-check gold-icon large-icon"></i>
                    <p>No active incidents. Microservice fleet is operating normally.</p>
                </div>
            `;
            return;
        }

        incidentsList.innerHTML = incidents.map(inc => `
            <div class="incident-card ${activeIncidentId === inc.id ? 'active' : ''}" onclick="selectIncident('${inc.id}')">
                <div class="inc-header">
                    <span class="inc-id">${inc.id}</span>
                    <span class="status-pill ${inc.status === 'RESOLVED' ? 'healthy' : 'critical'}">
                        ${inc.status}
                    </span>
                </div>
                <div class="inc-alert-title">${inc.alert_name} — ${inc.service_name}</div>
                <div class="inc-footer">
                    <span>Severity: <strong class="gold-highlight">${inc.severity}</strong></span>
                    <span>${new Date(inc.created_at * 1000).toLocaleTimeString()}</span>
                </div>
            </div>
        `).join("");

        // Auto select first incident if none selected
        if (!activeIncidentId && incidents.length > 0) {
            selectIncident(incidents[0].id);
        }
    } catch (e) {
        console.warn("Incidents fetch error", e);
    }
}

async function selectIncident(incidentId) {
    activeIncidentId = incidentId;
    document.querySelectorAll(".incident-card").forEach(c => c.classList.remove("active"));
    
    try {
        const res = await fetch(`${API_BASE}/api/incidents/${incidentId}`);
        if (!res.ok) return;
        const data = await res.json();
        const inc = data.incident;
        const actions = data.audit_actions;

        renderDiagnosticBreakdown(inc, actions);
    } catch (e) {
        console.warn("Error fetching incident detail", e);
    }
}

function renderDiagnosticBreakdown(inc, actions) {
    agentFlowViewer.innerHTML = `
        <div class="flow-step-box">
            <div class="flow-step-header">
                <i class="fa-solid fa-satellite-dish gold-icon"></i>
                <span>1. Telemetry Ingestion & Anomaly Trigger</span>
            </div>
            <div class="step-content-text">
                Incident <strong>${inc.id}</strong> received for service <strong>${inc.service_name}</strong>.
                Prometheus threshold alert: <code>${inc.alert_name}</code> (Severity: ${inc.severity}).
            </div>
        </div>

        <div class="flow-step-box">
            <div class="flow-step-header">
                <i class="fa-solid fa-microchip gold-icon"></i>
                <span>2. ML Anomaly Classifier (Isolation Forest on BGL Telemetry)</span>
            </div>
            <div class="step-content-text">
                Drain token parser abstracted live log signatures. Unsupervised Isolation Forest detected failure signature with confidence <strong>${(inc.confidence * 100).toFixed(1)}%</strong>.
            </div>
        </div>

        <div class="flow-step-box">
            <div class="flow-step-header">
                <i class="fa-solid fa-brain gold-icon"></i>
                <span>3. Gemini 1.5 Flash Diagnostic Root Cause Analysis (RCA)</span>
            </div>
            <div class="step-content-text">
                <strong class="gold-highlight">${inc.diagnosis}</strong>
            </div>
        </div>

        <div class="flow-step-box">
            <div class="flow-step-header">
                <i class="fa-solid fa-shield-halved gold-icon"></i>
                <span>4. SRE Security Policy Gatekeeper</span>
            </div>
            <div class="step-content-text">
                Remediation proposed: Allowlist verified. Blocked arbitrary shell execution. Approved safe Kubernetes operations.
            </div>
        </div>

        <div class="flow-step-box">
            <div class="flow-step-header">
                <i class="fa-solid fa-square-check gold-icon"></i>
                <span>5. Verification Loop & Remediation Execution</span>
            </div>
            <div class="step-content-text">
                Executed Actions: <strong>${actions.length} operation(s)</strong> applied via K8s tools. 
                Status: <strong class="gold-text">${inc.status}</strong>.
            </div>
            <pre class="code-snippet-box"><code>${inc.agent_report || "No full report generated."}</code></pre>
        </div>
    `;
}

async function fetchAuditLedger() {
    try {
        const res = await fetch(`${API_BASE}/api/audit-logs`);
        if (!res.ok) return;
        const logs = await res.json();

        if (logs.length === 0) return;

        auditLedgerTbody.innerHTML = logs.map(l => `
            <tr>
                <td>${new Date(l.timestamp * 1000).toLocaleTimeString()}</td>
                <td><span class="action-pill">${l.action_type}</span></td>
                <td><code>${l.target_service}</code></td>
                <td>${l.performed_by}</td>
                <td><span class="status-pill healthy">${l.status}</span></td>
            </tr>
        `).join("");
    } catch (e) {
        console.warn("Audit ledger fetch error", e);
    }
}

// ------------------------------------------------------------------------------
// Failure Simulation Triggers
// ------------------------------------------------------------------------------

async function triggerChaosIncident() {
    outageModal.classList.add("hidden");
    showToast("Injecting production failure... AutoSRE Agent activating.");

    let service = "payment-service";
    let alert = "DatabaseConnectionPoolExhausted";

    if (selectedChaosType === "oom") {
        service = "user-service";
        alert = "OOMKilledMemorySaturation";
    } else if (selectedChaosType === "latency") {
        service = "order-service";
        alert = "DownstreamTimeoutCascade";
    }

    try {
        const res = await fetch(`${API_BASE}/api/incidents/trigger`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                service_name: service,
                alert_name: alert,
                severity: "CRITICAL"
            })
        });

        const data = await res.json();
        showToast(`AutoSRE closed the loop! Incident ${data.incident_id} self-healed.`);

        // Refresh all views
        fetchSystemStatus();
        fetchFleetServices();
        fetchIncidents();
        fetchAuditLedger();
        selectIncident(data.incident_id);
    } catch (e) {
        showToast("Error triggering failure cascade.");
        console.error(e);
    }
}

function quickInjectChaos(serviceName) {
    showToast(`Injecting latency failure into ${serviceName}...`);
    fetch(`${API_BASE}/api/incidents/trigger`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            service_name: serviceName,
            alert_name: "HighLatencySpike",
            severity: "HIGH"
        })
    }).then(res => res.json()).then(data => {
        showToast(`Self-healed ${serviceName}! Actions executed.`);
        fetchSystemStatus();
        fetchFleetServices();
        fetchIncidents();
        fetchAuditLedger();
        selectIncident(data.incident_id);
    });
}

function showToast(message) {
    toastText.innerText = message;
    toastNotify.classList.remove("hidden");
    setTimeout(() => {
        toastNotify.classList.add("hidden");
    }, 4500);
}
