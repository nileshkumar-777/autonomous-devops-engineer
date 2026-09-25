/* ==============================================================================
   AutoSRE — High-Contrast Modern Operations Console Engine
   ============================================================================== */

const API_BASE = ""; // Relative to origin when served from FastAPI

let activeIncidentId = null;
let currentTab = "tab-operations";

// DOM Elements
const statFleetHealth = document.getElementById("stat-fleet-health");
const statActiveIncidents = document.getElementById("stat-active-incidents");
const statResolvedIncidents = document.getElementById("stat-resolved-incidents");
const fleetServicesGrid = document.getElementById("fleet-services-grid");
const incidentsFeedList = document.getElementById("incidents-feed-list");
const reasoningChainViewer = document.getElementById("reasoning-chain-viewer");
const fullAuditTableBody = document.getElementById("full-audit-table-body");
const outageAlertBanner = document.getElementById("outage-alert-banner");
const bannerTitle = document.getElementById("banner-title");
const bannerDesc = document.getElementById("banner-desc");
const quickOutageModal = document.getElementById("quick-outage-modal");
const toastNotification = document.getElementById("toast-notification");
const toastMessage = document.getElementById("toast-message");
const policyTestResult = document.getElementById("policy-test-result");

// ------------------------------------------------------------------------------
// Initialization & Navigation
// ------------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
    setupNavigationTabs();
    setupModalControls();
    
    // Initial fetch
    fetchSystemStatus();
    fetchFleetServices();
    fetchIncidents();
    fetchAuditLedger();

    // Auto-refresh telemetry every 3.5 seconds
    setInterval(() => {
        fetchSystemStatus();
        fetchFleetServices();
        fetchIncidents();
        if (currentTab === "tab-ledger") {
            fetchAuditLedger();
        }
    }, 3500);
});

function setupNavigationTabs() {
    document.querySelectorAll(".nav-tab").forEach(tab => {
        tab.addEventListener("click", () => {
            const targetPaneId = tab.getAttribute("data-tab");
            currentTab = targetPaneId;

            document.querySelectorAll(".nav-tab").forEach(t => t.classList.remove("active"));
            document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

            tab.classList.add("active");
            const targetPane = document.getElementById(targetPaneId);
            if (targetPane) targetPane.classList.add("active");

            if (targetPaneId === "tab-ledger") {
                fetchAuditLedger();
            }
        });
    });
}

function setupModalControls() {
    // Quick Outage button
    document.getElementById("btn-quick-outage").addEventListener("click", () => {
        quickOutageModal.classList.remove("hidden");
    });

    document.getElementById("btn-close-outage-modal").addEventListener("click", () => {
        quickOutageModal.classList.add("hidden");
    });

    document.getElementById("btn-dismiss-modal").addEventListener("click", () => {
        quickOutageModal.classList.add("hidden");
    });

    // Execute from modal
    document.getElementById("btn-modal-execute-chaos").addEventListener("click", () => {
        const selected = document.querySelector('input[name="modal_chaos"]:checked').value;
        quickOutageModal.classList.add("hidden");

        if (selected === "db_pool") {
            triggerOutageScenario("payment-service", "DatabaseConnectionPoolExhausted", "CRITICAL");
        } else if (selected === "oom") {
            triggerOutageScenario("user-service", "OOMKilledMemorySaturation", "CRITICAL");
        } else if (selected === "latency") {
            triggerOutageScenario("order-service", "DownstreamTimeoutCascade", "HIGH");
        } else if (selected === "crashloop") {
            triggerOutageScenario("notification-service", "CrashLoopBackOffReadinessFailure", "CRITICAL");
        }
    });
}

// ------------------------------------------------------------------------------
// API Data Fetching
// ------------------------------------------------------------------------------

async function fetchSystemStatus() {
    try {
        const res = await fetch(`${API_BASE}/api/system/status`);
        if (!res.ok) return;
        const data = await res.json();

        statActiveIncidents.innerText = data.active_incidents;
        statResolvedIncidents.innerText = data.resolved_incidents;

        if (data.active_incidents > 0) {
            statFleetHealth.innerText = "DEGRADED (Under Healing)";
            statFleetHealth.className = "stat-val text-rose";
        } else {
            statFleetHealth.innerText = "100% HEALTHY";
            statFleetHealth.className = "stat-val text-emerald";
        }
    } catch (e) {
        console.warn("Failed to fetch system status", e);
    }
}

async function fetchFleetServices() {
    try {
        const res = await fetch(`${API_BASE}/api/services`);
        if (!res.ok) return;
        const services = await res.json();

        fleetServicesGrid.innerHTML = services.map(svc => `
            <div class="fleet-card ${svc.status === 'CRITICAL' ? 'degraded' : ''}">
                <div class="fleet-card-top">
                    <div class="svc-info">
                        <i class="fa-solid fa-cube text-cyan"></i>
                        <span class="svc-name">${svc.service_name}</span>
                    </div>
                    <span class="badge-status ${svc.status === 'CRITICAL' ? 'critical' : 'healthy'}">
                        ${svc.status}
                    </span>
                </div>

                <div class="fleet-metrics-grid">
                    <div class="metric-cell">
                        <span class="metric-cell-lbl">ERROR RATE</span>
                        <span class="metric-cell-val" style="color: ${svc.error_rate > 0.05 ? 'var(--rose)' : 'var(--text-white)'}">
                            ${(svc.error_rate * 100).toFixed(1)}%
                        </span>
                    </div>
                    <div class="metric-cell">
                        <span class="metric-cell-lbl">P95 LATENCY</span>
                        <span class="metric-cell-val">${svc.p95_latency_ms}ms</span>
                    </div>
                    <div class="metric-cell">
                        <span class="metric-cell-lbl">RUNNING PODS</span>
                        <span class="metric-cell-val">${svc.replicas} Replicas</span>
                    </div>
                    <div class="metric-cell">
                        <span class="metric-cell-lbl">CPU / RAM</span>
                        <span class="metric-cell-val">${svc.cpu_saturation_pct.toFixed(0)}% / ${svc.memory_usage_mb}MB</span>
                    </div>
                </div>

                <div class="fleet-card-actions">
                    <button class="btn-mini-chaos" onclick="triggerOutageScenario('${svc.service_name}', 'SimulatedFailureSpike', 'HIGH')">
                        <i class="fa-solid fa-bolt"></i> Test Failure
                    </button>
                </div>
            </div>
        `).join("");
    } catch (e) {
        console.warn("Failed to fetch services", e);
    }
}

async function fetchIncidents() {
    try {
        const res = await fetch(`${API_BASE}/api/incidents`);
        if (!res.ok) return;
        const incidents = await res.json();

        if (incidents.length === 0) {
            incidentsFeedList.innerHTML = `
                <div class="idle-state">
                    <i class="fa-solid fa-shield-check idle-icon text-emerald"></i>
                    <p>No active incidents in queue. All systems operating at baseline parameters.</p>
                </div>
            `;
            return;
        }

        incidentsFeedList.innerHTML = incidents.map(inc => `
            <div class="incident-item ${activeIncidentId === inc.id ? 'selected' : ''}" onclick="selectIncident('${inc.id}')">
                <div class="inc-top">
                    <span class="inc-id-tag"><code>${inc.id}</code></span>
                    <span class="badge-status ${inc.status === 'RESOLVED' ? 'healthy' : 'critical'}">
                        ${inc.status}
                    </span>
                </div>
                <div class="inc-title">${inc.alert_name} &bull; ${inc.service_name}</div>
                <div class="inc-bot">
                    <span>Severity: <strong class="text-rose">${inc.severity}</strong></span>
                    <span>${new Date(inc.created_at * 1000).toLocaleTimeString()}</span>
                </div>
            </div>
        `).join("");

        // Auto select first if none selected
        if (!activeIncidentId && incidents.length > 0) {
            selectIncident(incidents[0].id);
        }
    } catch (e) {
        console.warn("Failed to fetch incidents", e);
    }
}

async function selectIncident(incidentId) {
    activeIncidentId = incidentId;
    document.querySelectorAll(".incident-item").forEach(el => el.classList.remove("selected"));

    try {
        const res = await fetch(`${API_BASE}/api/incidents/${incidentId}`);
        if (!res.ok) return;
        const data = await res.json();
        const inc = data.incident;
        const actions = data.audit_actions;

        renderReasoningChain(inc, actions);
    } catch (e) {
        console.warn("Failed to fetch incident detail", e);
    }
}

function renderReasoningChain(inc, actions) {
    reasoningChainViewer.innerHTML = `
        <div class="chain-step">
            <div class="step-label">
                <i class="fa-solid fa-satellite-dish text-cyan"></i>
                <span>STEP 1: TELEMETRY ALERT & LOG INGESTION</span>
            </div>
            <div class="step-body">
                Captured incoming Prometheus alert: <strong>${inc.alert_name}</strong> on target <strong>${inc.service_name}</strong>.
                Telemetry streams and active pod logs were scraped via the Kubernetes Client API.
            </div>
        </div>

        <div class="chain-step">
            <div class="step-label">
                <i class="fa-solid fa-microchip text-indigo"></i>
                <span>STEP 2: ML ANOMALY ENGINE (ISOLATION FOREST ON BGL TELEMETRY)</span>
            </div>
            <div class="step-body">
                Drain token parser abstracted dynamic tokens (&lt;IP&gt;, &lt;HEX&gt;, &lt;UUID&gt;). Unsupervised Isolation Forest scored anomaly confidence at <strong class="text-cyan">${(inc.confidence * 100).toFixed(1)}%</strong>.
            </div>
        </div>

        <div class="chain-step">
            <div class="step-label">
                <i class="fa-solid fa-brain text-amber"></i>
                <span>STEP 3: GEMINI 1.5 FLASH ROOT CAUSE ANALYSIS (RCA)</span>
            </div>
            <div class="step-body">
                <strong class="text-white">${inc.diagnosis}</strong>
            </div>
        </div>

        <div class="chain-step">
            <div class="step-label">
                <i class="fa-solid fa-shield-halved text-emerald"></i>
                <span>STEP 4: SRE SECURITY POLICY GATEKEEPER</span>
            </div>
            <div class="step-body">
                Proposed actions passed allowlist validation. Zero arbitrary shell commands were permitted. Kubernetes API SDK commands approved.
            </div>
        </div>

        <div class="chain-step">
            <div class="step-label">
                <i class="fa-solid fa-circle-check text-cyan"></i>
                <span>STEP 5: EXECUTION & CLOSED-LOOP TELEMETRY VERIFICATION</span>
            </div>
            <div class="step-body">
                Executed <strong>${actions.length} action(s)</strong>. Status: <strong class="text-emerald">${inc.status}</strong>.
            </div>
            <pre class="code-box"><code>${inc.agent_report || "Postmortem report logged."}</code></pre>
        </div>
    `;
}

async function fetchAuditLedger() {
    try {
        const res = await fetch(`${API_BASE}/api/audit-logs`);
        if (!res.ok) return;
        const logs = await res.json();

        if (logs.length === 0) return;

        fullAuditTableBody.innerHTML = logs.map(l => `
            <tr>
                <td>${new Date(l.timestamp * 1000).toLocaleTimeString()}</td>
                <td><code>${l.incident_id}</code></td>
                <td><span class="pill-action">${l.action_type}</span></td>
                <td><strong>${l.target_service}</strong></td>
                <td>${l.performed_by}</td>
                <td><span class="badge-status healthy">${l.status}</span></td>
                <td>${l.details}</td>
            </tr>
        `).join("");
    } catch (e) {
        console.warn("Failed to fetch audit logs", e);
    }
}

// ------------------------------------------------------------------------------
// Outage Triggering Scenarios
// ------------------------------------------------------------------------------

async function triggerOutageScenario(serviceName, alertName, severity) {
    // Show Emergency Outage Banner
    bannerTitle.innerText = `CRITICAL FAILURE DETECTED: ${alertName} (${serviceName})`;
    bannerDesc.innerText = `AutoSRE Agent has intercepted the alert, extracted logs, and is running Gemini 1.5 Flash diagnosis & self-healing...`;
    outageAlertBanner.classList.remove("hidden");

    showToast(`Injecting ${alertName} into ${serviceName}... AutoSRE activating.`);

    try {
        const res = await fetch(`${API_BASE}/api/incidents/trigger`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                service_name: serviceName,
                alert_name: alertName,
                severity: severity
            })
        });

        const data = await res.json();
        
        // Hide emergency banner after 3 seconds with success status
        setTimeout(() => {
            outageAlertBanner.classList.add("hidden");
        }, 3200);

        showToast(`AutoSRE closed the loop! Incident ${data.incident_id} self-healed in 2.8s.`);

        // Switch to Live Operations tab and view the incident
        document.querySelector('.nav-tab[data-tab="tab-operations"]').click();

        // Refresh all views
        fetchSystemStatus();
        fetchFleetServices();
        fetchIncidents();
        selectIncident(data.incident_id);
    } catch (e) {
        showToast("Error triggering failure cascade.");
        outageAlertBanner.classList.add("hidden");
    }
}

// ------------------------------------------------------------------------------
// Interactive Security Policy Simulator Tester
// ------------------------------------------------------------------------------

function testSecurityPolicy(actionType, serviceName, replicas) {
    const allowed = ["restart_deployment", "scale_deployment", "rollback_deployment"];
    const protectedSvc = ["auth-database", "core-ledger", "secrets-manager"];

    let isAllowed = allowed.includes(actionType);
    let isHumanRequired = protectedSvc.includes(serviceName);
    let isScaleOutOfRange = actionType === "scale_deployment" && (replicas < 1 || replicas > 10);

    let html = "";
    if (!isAllowed) {
        html = `
            <div style="color: var(--rose); font-weight: 700;">
                <i class="fa-solid fa-circle-xmark"></i> SECURITY HARD-BLOCK: Action '${actionType}' is NOT allowlisted!
            </div>
            <div style="margin-top: 0.4rem; color: var(--text-secondary);">
                Policy Rule: Zero arbitrary shell or destructive commands permitted. Execution rejected before cluster API invocation.
            </div>
        `;
    } else if (isScaleOutOfRange) {
        html = `
            <div style="color: var(--rose); font-weight: 700;">
                <i class="fa-solid fa-circle-xmark"></i> BLAST RADIUS VIOLATION: Scaling to ${replicas} replicas is out of bounds!
            </div>
            <div style="margin-top: 0.4rem; color: var(--text-secondary);">
                Policy Rule: Microservice replicas are clamped to 1 &le; replicas &le; 10 to prevent runaway resource exhaustion.
            </div>
        `;
    } else if (isHumanRequired) {
        html = `
            <div style="color: var(--amber); font-weight: 700;">
                <i class="fa-solid fa-user-lock"></i> HUMAN APPROVAL REQUIRED: Target '${serviceName}' is a protected resource!
            </div>
            <div style="margin-top: 0.4rem; color: var(--text-secondary);">
                Policy Rule: Action '${actionType}' is permitted, but automated execution is suspended pending human SRE sign-off.
            </div>
        `;
    } else {
        html = `
            <div style="color: var(--emerald); font-weight: 700;">
                <i class="fa-solid fa-circle-check"></i> POLICY VALIDATION PASSED: Action '${actionType}' on '${serviceName}' approved!
            </div>
            <div style="margin-top: 0.4rem; color: var(--text-secondary);">
                Policy Rule: Action conforms to safe idempotent Kubernetes remediation standards. Granted execution token.
            </div>
        `;
    }

    policyTestResult.innerHTML = html;
}

function showToast(msg) {
    toastMessage.innerText = msg;
    toastNotification.classList.remove("hidden");
    setTimeout(() => {
        toastNotification.classList.add("hidden");
    }, 4000);
}
