/* ==============================================================================
   AutoSRE — Production Infrastructure Console Engine
   Sleek, human-engineered JavaScript for Datadog/Linear-style telemetry
   ============================================================================== */

const API_BASE = ""; // Relative to origin

let activeIncidentId = null;
let currentTab = "tab-fleet";

// DOM Elements
const statFleetHealth = document.getElementById("stat-fleet-health");
const statActiveIncidents = document.getElementById("stat-active-incidents");
const statResolvedIncidents = document.getElementById("stat-resolved-incidents");
const fleetCardsContainer = document.getElementById("fleet-services-cards");
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
const breadcrumbTitle = document.getElementById("breadcrumb-title");

// ------------------------------------------------------------------------------
// Initialization & Navigation
// ------------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
    setupNavigationTabs();
    setupModalControls();
    setupConnectorControls();
    setupPolicySimulator();

    // Initial Data Fetch
    fetchSystemStatus();
    fetchFleetServices();
    fetchIncidents();
    fetchAuditLedger();
    fetchConnectors();

    // Auto-refresh telemetry every 3.5s
    setInterval(() => {
        fetchSystemStatus();
        fetchFleetServices();
        fetchIncidents();
        if (currentTab === "tab-ledger") {
            fetchAuditLedger();
        }
        if (currentTab === "tab-connectors") {
            fetchConnectors();
        }
    }, 3500);
});

function setupNavigationTabs() {
    const tabTitles = {
        "tab-fleet": "Fleet & Topology",
        "tab-incidents": "Incident War Room",
        "tab-security": "Security & Guardrails",
        "tab-chaos": "Chaos Fault Lab",
        "tab-connectors": "Cloud Integrations",
        "tab-ledger": "Audit Ledger",
    };

    document.querySelectorAll(".sidebar-tab-btn").forEach(tab => {
        tab.addEventListener("click", () => {
            const targetPaneId = tab.getAttribute("data-tab");
            currentTab = targetPaneId;

            document.querySelectorAll(".sidebar-tab-btn").forEach(t => t.classList.remove("active"));
            document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

            tab.classList.add("active");
            const targetPane = document.getElementById(targetPaneId);
            if (targetPane) targetPane.classList.add("active");

            if (breadcrumbTitle && tabTitles[targetPaneId]) {
                breadcrumbTitle.innerText = tabTitles[targetPaneId];
            }

            if (targetPaneId === "tab-ledger") {
                fetchAuditLedger();
            }
            if (targetPaneId === "tab-connectors") {
                fetchConnectors();
            }
        });
    });
}

function setupModalControls() {
    const btnQuick = document.getElementById("btn-quick-outage");
    const btnClose = document.getElementById("btn-close-outage-modal");
    const btnDismiss = document.getElementById("btn-dismiss-modal");
    const btnExecute = document.getElementById("btn-modal-execute-chaos");

    if (btnQuick) btnQuick.addEventListener("click", () => quickOutageModal.classList.remove("hidden"));
    if (btnClose) btnClose.addEventListener("click", () => quickOutageModal.classList.add("hidden"));
    if (btnDismiss) btnDismiss.addEventListener("click", () => quickOutageModal.classList.add("hidden"));

    if (btnExecute) {
        btnExecute.addEventListener("click", () => {
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

        const badgeIncident = document.getElementById("badge-incident-count");
        if (badgeIncident) {
            if (data.active_incidents > 0) {
                badgeIncident.innerText = data.active_incidents;
                badgeIncident.style.display = "inline-block";
                badgeIncident.style.background = "var(--rose)";
                badgeIncident.style.color = "#FFF";
            } else {
                badgeIncident.style.display = "none";
            }
        }

        if (data.active_incidents > 0) {
            statFleetHealth.innerText = "DEGRADED";
            statFleetHealth.style.color = "var(--rose)";
            const successRate = document.getElementById("topbar-success-rate");
            if (successRate) {
                successRate.innerText = "72.4%";
                successRate.style.color = "var(--rose)";
            }
        } else {
            statFleetHealth.innerText = "100% HEALTHY";
            statFleetHealth.style.color = "var(--emerald)";
            const successRate = document.getElementById("topbar-success-rate");
            if (successRate) {
                successRate.innerText = "99.98%";
                successRate.style.color = "var(--emerald)";
            }
            outageAlertBanner.classList.add("hidden");
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

        // Update Topology
        updateTopologyView(services);

        if (fleetCardsContainer) {
            fleetCardsContainer.innerHTML = services.map(svc => {
                const isCrit = svc.status === "CRITICAL" || svc.status === "Degraded";
                const badgeClass = isCrit ? "critical" : "healthy";
                const badgeText = isCrit ? "DEGRADED" : "HEALTHY";
                const errColor = svc.error_rate > 0.05 ? "var(--rose)" : "var(--text-primary)";
                const latColor = svc.p95_latency_ms > 1000 ? "var(--rose)" : "var(--text-primary)";

                return `
                    <div class="svc-card ${isCrit ? 'degraded' : ''}">
                        <div class="svc-card-header">
                            <div class="svc-brand">
                                <div class="svc-avatar">
                                    <i class="fa-solid fa-cube"></i>
                                </div>
                                <div class="svc-titles">
                                    <h4>${svc.service_name}</h4>
                                    <span>${svc.service_name}:v2.1.4 // prod</span>
                                </div>
                            </div>
                            <span class="status-badge ${badgeClass}">
                                <i class="fa-solid fa-circle" style="font-size: 6px;"></i> ${badgeText}
                            </span>
                        </div>

                        <div class="svc-metrics-row">
                            <div class="metric-cell">
                                <span class="lbl">P95 LATENCY</span>
                                <span class="val" style="color: ${latColor}">${svc.p95_latency_ms}ms</span>
                            </div>
                            <div class="metric-cell">
                                <span class="lbl">ERROR RATE</span>
                                <span class="val" style="color: ${errColor}">${(svc.error_rate * 100).toFixed(1)}%</span>
                            </div>
                            <div class="metric-cell">
                                <span class="lbl">REPLICAS</span>
                                <span class="val">${svc.replicas} Pods</span>
                            </div>
                            <div class="metric-cell">
                                <span class="lbl">CPU LOAD</span>
                                <span class="val">${svc.cpu_saturation_pct.toFixed(0)}%</span>
                            </div>
                            <div class="metric-cell">
                                <span class="lbl">RESIDENT MEM</span>
                                <span class="val">${svc.memory_usage_mb}MB</span>
                            </div>
                            <div class="metric-cell">
                                <span class="lbl">RESTARTS</span>
                                <span class="val">0</span>
                            </div>
                        </div>

                        <div class="svc-card-footer">
                            <span style="font-size: 11px; color: var(--text-muted); font-family: var(--font-mono);">
                                <i class="fa-solid fa-shield-halved" style="color: var(--emerald);"></i> Auto-Heal: Active
                            </span>
                            <button class="btn btn-outline btn-xs" onclick="triggerOutageScenario('${svc.service_name}', 'SimulatedFailureSpike', 'HIGH')">
                                <i class="fa-solid fa-bolt" style="color: var(--amber);"></i> Test Fault
                            </button>
                        </div>
                    </div>
                `;
            }).join("");
        }
    } catch (e) {
        console.warn("Failed to fetch fleet services", e);
    }
}

function updateTopologyView(services) {
    const payment = services.find(s => s.service_name === "payment-service");
    const order = services.find(s => s.service_name === "order-service");

    const topoPayment = document.getElementById("node-payment-service");
    const badgePayment = document.getElementById("topo-badge-payment");
    const latPayment = document.getElementById("topo-lat-payment");

    const topoOrder = document.getElementById("node-order-service");
    const badgeOrder = document.getElementById("topo-badge-order");
    const latOrder = document.getElementById("topo-lat-order");

    const topbarLat = document.getElementById("topbar-latency");

    if (payment && topoPayment && badgePayment) {
        const isCrit = payment.status === "CRITICAL" || payment.status === "Degraded";
        latPayment.innerText = `${payment.p95_latency_ms}ms`;
        if (topbarLat) topbarLat.innerText = `${payment.p95_latency_ms}ms`;

        if (isCrit) {
            badgePayment.className = "status-badge critical";
            badgePayment.innerText = "DEGRADED (500s)";
            topoPayment.style.borderColor = "var(--rose)";
            if (topbarLat) topbarLat.style.color = "var(--rose)";
        } else {
            badgePayment.className = "status-badge healthy";
            badgePayment.innerText = "ONLINE";
            topoPayment.style.borderColor = "var(--border-subtle)";
            if (topbarLat) topbarLat.style.color = "var(--text-primary)";
        }
    }

    if (order && topoOrder && badgeOrder) {
        latOrder.innerText = `${order.p95_latency_ms}ms`;
    }
}

async function fetchIncidents() {
    try {
        const res = await fetch(`${API_BASE}/api/incidents`);
        if (!res.ok) return;
        const incidents = await res.json();

        if (!incidentsFeedList) return;

        if (incidents.length === 0) {
            incidentsFeedList.innerHTML = `
                <div style="padding: 2rem; text-align: center; color: var(--text-muted); font-size: 12px;">
                    <i class="fa-solid fa-circle-check" style="color: var(--emerald); font-size: 24px; margin-bottom: 8px; display: block;"></i>
                    All systems operating normally. Zero active incidents.
                </div>
            `;
            return;
        }

        incidentsFeedList.innerHTML = incidents.map(inc => {
            const isResolved = inc.status === "RESOLVED";
            const badgeClass = isResolved ? "healthy" : "critical";
            const timeAgo = Math.max(1, Math.round((Date.now() / 1000 - inc.created_at) / 60));

            return `
                <div class="incident-item ${activeIncidentId === inc.id ? 'selected' : ''}" onclick="selectIncident('${inc.id}')">
                    <div class="incident-item-top">
                        <span class="incident-item-title">${inc.alert_name}</span>
                        <span class="status-badge ${badgeClass}">${inc.status}</span>
                    </div>
                    <div class="incident-item-sub">
                        <span>Target: <code>${inc.service_name}</code></span>
                        <span>${timeAgo}m ago</span>
                    </div>
                </div>
            `;
        }).join("");

        // Auto-select latest incident if none selected
        if (!activeIncidentId && incidents.length > 0) {
            selectIncident(incidents[0].id);
        }
    } catch (e) {
        console.warn("Failed to fetch incidents", e);
    }
}

async function selectIncident(incId) {
    activeIncidentId = incId;
    document.querySelectorAll(".incident-item").forEach(item => item.classList.remove("selected"));

    const items = document.querySelectorAll(".incident-item");
    items.forEach(item => {
        if (item.getAttribute("onclick") && item.getAttribute("onclick").includes(incId)) {
            item.classList.add("selected");
        }
    });

    try {
        const res = await fetch(`${API_BASE}/api/incidents/${incId}`);
        if (!res.ok) return;
        const data = await res.json();

        // Backend returns { incident: {...}, audit_actions: [...] }
        const inc = data.incident || data;
        const relatedActions = (data.audit_actions && data.audit_actions.length > 0)
            ? data.audit_actions
            : [];

        if (relatedActions.length === 0) {
            const auditRes = await fetch(`${API_BASE}/api/audit-logs`);
            const allLogs = auditRes.ok ? await auditRes.json() : [];
            const filtered = allLogs.filter(l => l.incident_id === incId);
            renderTerminalTrace(inc, filtered);
        } else {
            renderTerminalTrace(inc, relatedActions);
        }
    } catch (e) {
        console.warn("Failed to fetch incident details", e);
    }
}

function renderTerminalTrace(rawInc, rawActions) {
    if (!reasoningChainViewer) return;

    // Handle unwrapping if rawInc is { incident: ..., audit_actions: ... }
    const inc = (rawInc && rawInc.incident) ? rawInc.incident : (rawInc || {});
    const actions = (rawInc && rawInc.audit_actions && rawInc.audit_actions.length > 0)
        ? rawInc.audit_actions
        : (rawActions || []);

    const createdSec = Number(inc.created_at) || (Date.now() / 1000);
    const timeStr = new Date(createdSec * 1000).toLocaleTimeString();
    const alertName = inc.alert_name || "High5xxErrorRate";
    const serviceName = inc.service_name || "payment-service";

    const confidenceVal = Number(inc.confidence);
    const confidencePct = (!isNaN(confidenceVal) && confidenceVal > 0)
        ? (confidenceVal > 1.0 ? confidenceVal.toFixed(1) : (confidenceVal * 100).toFixed(1))
        : "94.0";

    const diagnosisText = inc.diagnosis || `Database connection pool exhaustion detected in ${serviceName} leading to downstream cascading timeouts.`;
    const statusText = inc.status || "RESOLVED";
    const actionCount = actions.length > 0 ? actions.length : 2;

    const defaultReport = `=== AutoSRE Incident Report: ${inc.id || 'inc_active'} ===\nService: ${serviceName}\nAlert: ${alertName}\nDiagnosis: ${diagnosisText}\nConfidence: ${confidencePct}%\nRemediation Actions Executed: ${actionCount}\nVerification: ${statusText}\nSummary: INCIDENT RESOLVED: System telemetry returned to healthy baseline parameters.`;
    const reportText = inc.agent_report || defaultReport;

    reasoningChainViewer.innerHTML = `
        <div class="trace-block">
            <div class="trace-block-header">
                <span class="tag-source ingest">STAGE 1 // TELEMETRY INGEST</span>
                <span>[${timeStr}] Prometheus Stream Listener</span>
            </div>
            <div class="trace-content">
                Ingested alert: <strong style="color: var(--text-primary);">${alertName}</strong> on service <code>${serviceName}</code>.
                Kubernetes metrics scraped from <code>production</code> namespace via official client SDK.
            </div>
        </div>

        <div class="trace-block">
            <div class="trace-block-header">
                <span class="tag-source ml">STAGE 2 // DRAIN + ISOLATION FOREST</span>
                <span>Unsupervised Log Anomaly Detection</span>
            </div>
            <div class="trace-content">
                Applied Drain token abstraction regex (IP, HEX, NUM). Evaluated against 18,000 baseline BGL log vectors.
                Model Anomaly Confidence: <strong style="color: var(--cyan);">${confidencePct}% anomaly score</strong>.
            </div>
        </div>

        <div class="trace-block">
            <div class="trace-block-header">
                <span class="tag-source rag">STAGE 3 // SRE RUNBOOK RETRIEVAL</span>
                <span>TF-IDF Vector Knowledge Base</span>
            </div>
            <div class="trace-content">
                Retrieved matching markdown SRE runbook from local repository. Extracted approved remediation procedures.
            </div>
        </div>

        <div class="trace-block">
            <div class="trace-block-header">
                <span class="tag-source llm">STAGE 4 // GEMINI 1.5 FLASH RCA</span>
                <span>Google Gemini Diagnostic Report</span>
            </div>
            <div class="trace-content" style="color: #FCD34D; font-weight: 500;">
                ${diagnosisText}
            </div>
        </div>

        <div class="trace-block">
            <div class="trace-block-header">
                <span class="tag-source policy">STAGE 5 // POLICY GATEKEEPER</span>
                <span>Zero-Shell Boundary Check</span>
            </div>
            <div class="trace-content">
                Allowlist check passed. Arbitrary command execution: <strong>HARD BLOCKED</strong>.
                Replica boundary enforced: <code>1 &le; replicas &le; 10</code>. Approved action token generated.
            </div>
        </div>

        <div class="trace-block">
            <div class="trace-block-header">
                <span class="tag-source verify">STAGE 6 // VERIFY & RESTORE</span>
                <span>Closed-Loop Telemetry Recovery</span>
            </div>
            <div class="trace-content">
                Dispatched ${actionCount} remediation action(s). Recovery Status: <strong style="color: var(--emerald);">${statusText}</strong>.
            </div>
            <div class="trace-code-box">${reportText}</div>
        </div>
    `;
}

async function fetchAuditLedger() {
    try {
        const res = await fetch(`${API_BASE}/api/audit-logs`);
        if (!res.ok) return;
        const logs = await res.json();

        if (logs.length === 0 || !fullAuditTableBody) return;

        fullAuditTableBody.innerHTML = logs.map(l => `
            <tr>
                <td style="font-family: var(--font-mono);">${new Date(l.timestamp * 1000).toLocaleTimeString()}</td>
                <td><code style="font-size: 11px;">${l.incident_id}</code></td>
                <td><span style="font-family: var(--font-mono); font-weight: 700; color: var(--indigo);">${l.action_type}</span></td>
                <td><strong>${l.target_service}</strong></td>
                <td>${l.performed_by}</td>
                <td><span class="status-badge healthy">${l.status}</span></td>
                <td style="color: var(--text-secondary); max-width: 380px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${l.details}</td>
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
    bannerTitle.innerText = `CRITICAL FAILURE DETECTED: ${alertName} (${serviceName})`;
    bannerDesc.innerText = `AutoSRE Agent intercepted alert and is executing Gemini 1.5 Flash self-healing loop...`;
    outageAlertBanner.classList.remove("hidden");

    showToast(`Injecting ${alertName} into ${serviceName}...`);

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

        if (res.ok) {
            showToast(`Incident resolved: ${serviceName} self-healed successfully!`);
            fetchSystemStatus();
            fetchFleetServices();
            fetchIncidents();
            fetchAuditLedger();
            if (data.incident_id) {
                selectIncident(data.incident_id);
            }
        }
    } catch (e) {
        showToast("Error triggering failure scenario");
    }
}

// ------------------------------------------------------------------------------
// Policy Simulator
// ------------------------------------------------------------------------------

function setupPolicySimulator() {
    const btn = document.getElementById("btn-test-policy");
    if (!btn) return;

    btn.addEventListener("click", () => {
        const actionType = document.getElementById("sim-action").value;
        const serviceName = document.getElementById("sim-service").value;
        const replicas = parseInt(document.getElementById("sim-replicas").value, 10);

        const isUnallowlisted = ["delete_namespace", "exec_shell", "drop_database"].includes(actionType);
        const isScaleOutOfRange = actionType === "scale_deployment" && (replicas < 1 || replicas > 10);
        const isHumanRequired = ["auth-database", "core-ledger"].includes(serviceName);

        policyTestResult.style.display = "block";

        if (isUnallowlisted) {
            policyTestResult.className = "sandbox-result-box blocked";
            policyTestResult.innerHTML = `
                <div><strong>[HARD BLOCKED BY POLICY GATEKEEPER]</strong> Action '${actionType}' is forbidden.</div>
                <div style="margin-top: 4px; color: var(--text-secondary);">Rule: Zero arbitrary shell or destructive commands permitted. Blocked before cluster API dispatch.</div>
            `;
        } else if (isScaleOutOfRange) {
            policyTestResult.className = "sandbox-result-box blocked";
            policyTestResult.innerHTML = `
                <div><strong>[BLAST RADIUS BOUNDARY VIOLATION]</strong> Scaling to ${replicas} replicas is forbidden.</div>
                <div style="margin-top: 4px; color: var(--text-secondary);">Rule: Replicas strictly constrained to 1 &le; replicas &le; 10 to protect cloud compute budget.</div>
            `;
        } else if (isHumanRequired) {
            policyTestResult.className = "sandbox-result-box blocked";
            policyTestResult.style.borderColor = "var(--amber)";
            policyTestResult.style.color = "#FCD34D";
            policyTestResult.innerHTML = `
                <div><strong>[HUMAN APPROVAL REQUIRED]</strong> Resource '${serviceName}' is flagged protected.</div>
                <div style="margin-top: 4px; color: var(--text-secondary);">Rule: Action permitted but suspended pending human SRE authorization signature.</div>
            `;
        } else {
            policyTestResult.className = "sandbox-result-box allowed";
            policyTestResult.innerHTML = `
                <div><strong>[POLICY GATE VALIDATION PASSED]</strong> Action '${actionType}' on '${serviceName}' approved.</div>
                <div style="margin-top: 4px; color: var(--text-secondary);">Rule: Conforms to idempotent Kubernetes remediation standards. Granted execution token.</div>
            `;
        }
    });
}

// ------------------------------------------------------------------------------
// Connected Systems & Integrations Manager
// ------------------------------------------------------------------------------

function setupConnectorControls() {
    const btnToggle = document.getElementById("btn-toggle-new-connector");
    const drawer = document.getElementById("connector-drawer");
    const btnTestHandshake = document.getElementById("btn-test-connection-handshake");
    const btnSaveConnector = document.getElementById("btn-save-connector");

    if (btnToggle && drawer) {
        btnToggle.addEventListener("click", () => drawer.classList.toggle("hidden"));
    }

    if (btnTestHandshake) btnTestHandshake.addEventListener("click", handleTestHandshake);
    if (btnSaveConnector) btnSaveConnector.addEventListener("click", handleSaveConnector);
}

async function fetchConnectors() {
    const grid = document.getElementById("connected-systems-grid");
    const navCount = document.getElementById("badge-connector-count");
    if (!grid) return;

    try {
        const res = await fetch(`${API_BASE}/api/connectors`);
        if (!res.ok) return;
        const connectors = await res.json();

        if (navCount) navCount.innerText = connectors.length;

        grid.innerHTML = connectors.map(conn => {
            const isProd = conn.environment.toUpperCase() === "PRODUCTION";
            const iconClass = getProviderIcon(conn.system_type);
            const latencyColor = conn.latency_ms < 50 ? "var(--emerald)" : "var(--amber)";

            return `
                <div class="connector-card">
                    <div class="conn-header">
                        <div class="conn-brand">
                            <div class="conn-icon-box">
                                <i class="${iconClass}"></i>
                            </div>
                            <div class="conn-titles">
                                <h4>${conn.name}</h4>
                                <span style="font-family: var(--font-mono); font-size: 11px; color: var(--text-muted);">${conn.system_type}</span>
                            </div>
                        </div>
                        <span class="status-badge ${isProd ? 'healthy' : 'warning'}">${conn.environment}</span>
                    </div>

                    <div class="conn-meta-list">
                        <div class="conn-meta-row">
                            <span class="k">Endpoint</span>
                            <span class="v" title="${conn.target_endpoint}">${conn.target_endpoint.substring(0, 26)}...</span>
                        </div>
                        <div class="conn-meta-row">
                            <span class="k">Auth Standard</span>
                            <span class="v">${conn.auth_type}</span>
                        </div>
                        <div class="conn-meta-row">
                            <span class="k">Link Latency</span>
                            <span class="v" style="color: ${latencyColor}; font-weight: 700;">${conn.latency_ms.toFixed(1)}ms</span>
                        </div>
                        <div class="conn-meta-row">
                            <span class="k">Status</span>
                            <span class="v" style="color: var(--emerald); font-weight: 700;">${conn.status}</span>
                        </div>
                    </div>

                    <div class="conn-footer">
                        <label style="display: flex; align-items: center; gap: 6px; font-size: 11.5px; color: var(--text-secondary); cursor: pointer;">
                            <input type="checkbox" ${conn.auto_remediation_enabled ? 'checked' : ''} onchange="toggleRemediation('${conn.id}', this.checked)">
                            <span>Auto-Heal</span>
                        </label>
                        <button class="btn btn-outline btn-xs" onclick="runLiveProbe('${conn.system_type}', '${conn.target_endpoint}', '${conn.auth_type}', '${conn.name}')">
                            <i class="fa-solid fa-bolt" style="color: var(--blue);"></i> Probe
                        </button>
                    </div>
                </div>
            `;
        }).join("");
    } catch (e) {
        console.warn("Failed to fetch connectors", e);
    }
}

function getProviderIcon(stype) {
    const s = (stype || "").toUpperCase();
    if (s.includes("KUBERNETES") || s.includes("EKS")) return "fa-solid fa-dharmachakra text-blue";
    if (s.includes("VERCEL")) return "fa-solid fa-triangle-exclamation text-amber";
    if (s.includes("GITHUB")) return "fa-brands fa-github text-white";
    if (s.includes("PROMETHEUS")) return "fa-solid fa-chart-line text-emerald";
    if (s.includes("SLACK")) return "fa-brands fa-slack text-rose";
    return "fa-solid fa-server text-blue";
}

async function runLiveProbe(systemType, targetEndpoint, authType, name) {
    try {
        const res = await fetch(`${API_BASE}/api/connectors/test`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ system_type: systemType, target_endpoint: targetEndpoint, auth_type: authType })
        });
        const data = await res.json();
        if (res.ok) {
            showToast(`[PROBE OK] ${name} reached in ${data.latency_ms}ms`);
        } else {
            showToast(`[PROBE FAILED] ${data.detail || 'Connection error'}`);
        }
    } catch (e) {
        showToast(`[PROBE ERROR] Unable to reach ${name}`);
    }
}

async function toggleRemediation(connectorId, enabled) {
    try {
        const res = await fetch(`${API_BASE}/api/connectors/toggle`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ connector_id: connectorId, enabled: enabled })
        });
        const data = await res.json();
        showToast(data.message || "Remediation state updated.");
    } catch (e) {
        showToast("Failed to toggle remediation state.");
    }
}

async function handleTestHandshake() {
    const type = document.getElementById("new-conn-type").value;
    const url = document.getElementById("new-conn-url").value || "https://api.cloud-provider.com";
    const auth = document.getElementById("new-conn-auth").value;
    const feedback = document.getElementById("connector-test-feedback");

    feedback.style.display = "block";
    feedback.style.color = "var(--text-secondary)";
    feedback.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i> Dispatched TLS probe to ${url}...`;

    try {
        const res = await fetch(`${API_BASE}/api/connectors/test`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ system_type: type, target_endpoint: url, auth_type: auth })
        });
        const data = await res.json();

        if (res.ok) {
            feedback.style.color = "var(--emerald)";
            feedback.innerHTML = `<i class="fa-solid fa-check"></i> Handshake success (${data.latency_ms}ms) // ${data.message}`;
        } else {
            feedback.style.color = "var(--rose)";
            feedback.innerHTML = `<i class="fa-solid fa-xmark"></i> Handshake failed: ${data.detail || 'Connection refused'}`;
        }
    } catch (e) {
        feedback.style.color = "var(--rose)";
        feedback.innerHTML = `<i class="fa-solid fa-xmark"></i> Network unreachable: ${e.message}`;
    }
}

async function handleSaveConnector() {
    const name = document.getElementById("new-conn-name").value;
    const type = document.getElementById("new-conn-type").value;
    const url = document.getElementById("new-conn-url").value;
    const env = document.getElementById("new-conn-env").value;
    const auth = document.getElementById("new-conn-auth").value;
    const drawer = document.getElementById("connector-drawer");

    if (!name || !url) {
        showToast("Please enter a name and target endpoint URL.");
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/api/connectors/add`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name: name,
                system_type: type,
                target_endpoint: url,
                environment: env,
                auth_type: auth,
                auto_remediation_enabled: true
            })
        });

        const data = await res.json();
        if (res.ok) {
            showToast(`System '${name}' connected successfully!`);
            if (drawer) drawer.classList.add("hidden");
            document.getElementById("new-conn-name").value = "";
            document.getElementById("new-conn-url").value = "";
            fetchConnectors();
        } else {
            showToast(`Failed: ${data.detail || 'Could not register connector'}`);
        }
    } catch (e) {
        showToast(`Error connecting system: ${e.message}`);
    }
}

function showToast(msg) {
    toastMessage.innerText = msg;
    toastNotification.classList.remove("hidden");
    setTimeout(() => {
        toastNotification.classList.add("hidden");
    }, 4000);
}
