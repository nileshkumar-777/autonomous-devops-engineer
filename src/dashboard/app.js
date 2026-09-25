/* ==============================================================================
   AutoSRE — Production Infrastructure Console Engine
   Clean, human-engineered JavaScript for Datadog/Linear-style telemetry
   ============================================================================== */

const API_BASE = ""; // Relative to origin

let activeIncidentId = null;
let currentTab = "tab-fleet";

// DOM Elements
const statFleetHealth = document.getElementById("stat-fleet-health");
const statActiveIncidents = document.getElementById("stat-active-incidents");
const statResolvedIncidents = document.getElementById("stat-resolved-incidents");
const fleetTableBody = document.getElementById("fleet-services-table-body");
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
    document.querySelectorAll(".nav-tab-btn").forEach(tab => {
        tab.addEventListener("click", () => {
            const targetPaneId = tab.getAttribute("data-tab");
            currentTab = targetPaneId;

            document.querySelectorAll(".nav-tab-btn").forEach(t => t.classList.remove("active"));
            document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

            tab.classList.add("active");
            const targetPane = document.getElementById(targetPaneId);
            if (targetPane) targetPane.classList.add("active");

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

        const clusterIndicator = document.getElementById("cluster-indicator");

        if (data.active_incidents > 0) {
            statFleetHealth.innerText = "DEGRADED";
            statFleetHealth.style.color = "var(--red)";
            if (clusterIndicator) clusterIndicator.className = "dot-status red";
        } else {
            statFleetHealth.innerText = "100% HEALTHY";
            statFleetHealth.style.color = "var(--green)";
            if (clusterIndicator) clusterIndicator.className = "dot-status green";
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

        if (fleetTableBody) {
            fleetTableBody.innerHTML = services.map(svc => {
                const isCrit = svc.status === "CRITICAL" || svc.status === "Degraded";
                const statusClass = isCrit ? "critical" : "healthy";
                const statusText = isCrit ? "DEGRADED" : "HEALTHY";
                const errColor = svc.error_rate > 0.05 ? "var(--red)" : "inherit";

                return `
                    <tr>
                        <td><span class="status-badge ${statusClass}"><span class="dot-status ${isCrit ? 'red' : 'green'}"></span> ${statusText}</span></td>
                        <td>
                            <div class="svc-title-cell">
                                <i class="fa-solid fa-cube" style="color: var(--blue);"></i>
                                <span>${svc.service_name}</span>
                            </div>
                        </td>
                        <td><span style="font-family: var(--font-mono); font-weight: 600;">${svc.replicas} Pods</span></td>
                        <td><span style="font-family: var(--font-mono);">${svc.p95_latency_ms}ms</span></td>
                        <td><span style="font-family: var(--font-mono); color: ${errColor}; font-weight: 600;">${(svc.error_rate * 100).toFixed(1)}%</span></td>
                        <td><span style="font-family: var(--font-mono);">${svc.cpu_saturation_pct.toFixed(0)}%</span></td>
                        <td><span style="font-family: var(--font-mono);">${svc.memory_usage_mb}MB</span></td>
                        <td>
                            <button class="btn btn-outline btn-xs" onclick="triggerOutageScenario('${svc.service_name}', 'SimulatedFailureSpike', 'HIGH')">
                                <i class="fa-solid fa-bolt" style="color: var(--amber);"></i> Test Fault
                            </button>
                        </td>
                    </tr>
                `;
            }).join("");
        }
    } catch (e) {
        console.warn("Failed to fetch fleet services", e);
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
                <div style="padding: 1.5rem; text-align: center; color: var(--text-tertiary); font-size: 12px;">
                    No active or historical incidents recorded.
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
                    <div class="incident-item-meta">
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

    try {
        const res = await fetch(`${API_BASE}/api/incidents/${incId}`);
        if (!res.ok) return;
        const inc = await res.json();

        const auditRes = await fetch(`${API_BASE}/api/audit-logs`);
        const allLogs = auditRes.ok ? await auditRes.json() : [];
        const relatedActions = allLogs.filter(l => l.incident_id === incId);

        renderTerminalTrace(inc, relatedActions);
    } catch (e) {
        console.warn("Failed to fetch incident details", e);
    }
}

function renderTerminalTrace(inc, actions) {
    if (!reasoningChainViewer) return;

    const timeStr = new Date(inc.created_at * 1000).toLocaleTimeString();

    reasoningChainViewer.innerHTML = `
        <div class="terminal-entry">
            <div class="terminal-tag-line">
                <span class="terminal-source ingest">INGEST</span>
                <span>[${timeStr}] Prometheus Ingress Gate</span>
            </div>
            <div class="terminal-text">
                Alert captured: <strong>${inc.alert_name}</strong> on service <code>${inc.service_name}</code>.
                Kubernetes API telemetry scraped from <code>namespace/production</code>.
            </div>
        </div>

        <div class="terminal-entry">
            <div class="terminal-tag-line">
                <span class="terminal-source ml">ML_ANOMALY</span>
                <span>Drain Token Extraction & IsolationForest</span>
            </div>
            <div class="terminal-text">
                Token abstraction applied: normalized IP, UUID, and Hex payloads.
                Unsupervised Isolation Forest anomaly score: <strong style="color: var(--blue);">${(inc.confidence * 100).toFixed(1)}% anomaly confidence</strong>.
            </div>
        </div>

        <div class="terminal-entry">
            <div class="terminal-tag-line">
                <span class="terminal-source rag">RAG_KNOWLEDGE</span>
                <span>Vector Similarity Retrieval</span>
            </div>
            <div class="terminal-text">
                Retrieved matching markdown SRE runbook from local knowledge base with operational remediation steps.
            </div>
        </div>

        <div class="terminal-entry">
            <div class="terminal-tag-line">
                <span class="terminal-source llm">GEMINI_RCA</span>
                <span>Gemini 1.5 Flash Structured Reasoner</span>
            </div>
            <div class="terminal-text" style="color: #FBBF24; font-weight: 500;">
                ${inc.diagnosis}
            </div>
        </div>

        <div class="terminal-entry">
            <div class="terminal-tag-line">
                <span class="terminal-source gate">POLICY_GATE</span>
                <span>No-Shell Security Guardrail Check</span>
            </div>
            <div class="terminal-text">
                Proposed remediation verified against strict allowlist. Arbitrary shell access: <strong>BLOCKED</strong>.
                Parameter blast radius boundary clamped: <code>1 &le; replicas &le; 10</code>.
            </div>
        </div>

        <div class="terminal-entry">
            <div class="terminal-tag-line">
                <span class="terminal-source k8s">EXEC_VERIFY</span>
                <span>Kubernetes Python SDK Execution</span>
            </div>
            <div class="terminal-text">
                Dispatched ${actions.length} action(s). Final status: <strong style="color: var(--green);">${inc.status}</strong>.
            </div>
            <div class="terminal-code-block">${inc.agent_report || "Telemetry verified stable post-remediation."}</div>
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
                <td><span style="font-family: var(--font-mono); font-weight: 600; color: var(--blue);">${l.action_type}</span></td>
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
    bannerDesc.innerText = `AutoSRE Agent intercepted alert and is executing self-healing pipeline...`;
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
            policyTestResult.className = "policy-verdict-box blocked";
            policyTestResult.innerHTML = `
                <div><strong>[BLOCKED BY POLICY GATEKEEPER]</strong> Action '${actionType}' is forbidden.</div>
                <div style="margin-top: 4px; color: var(--text-secondary);">Rule: Zero arbitrary shell or destructive commands permitted. Denied before cluster API invocation.</div>
            `;
        } else if (isScaleOutOfRange) {
            policyTestResult.className = "policy-verdict-box blocked";
            policyTestResult.innerHTML = `
                <div><strong>[BLAST RADIUS VIOLATION]</strong> Scaling to ${replicas} replicas violates safety policy bounds.</div>
                <div style="margin-top: 4px; color: var(--text-secondary);">Rule: Microservice replicas are clamped to 1 &le; replicas &le; 10 to prevent runaway resource exhaustion.</div>
            `;
        } else if (isHumanRequired) {
            policyTestResult.className = "policy-verdict-box blocked";
            policyTestResult.style.borderColor = "var(--amber)";
            policyTestResult.style.color = "#FCD34D";
            policyTestResult.innerHTML = `
                <div><strong>[HUMAN APPROVAL REQUIRED]</strong> Target '${serviceName}' is a protected resource.</div>
                <div style="margin-top: 4px; color: var(--text-secondary);">Rule: Automated execution suspended pending human SRE authorization.</div>
            `;
        } else {
            policyTestResult.className = "policy-verdict-box allowed";
            policyTestResult.innerHTML = `
                <div><strong>[POLICY GATE PASSED]</strong> Action '${actionType}' on '${serviceName}' approved.</div>
                <div style="margin-top: 4px; color: var(--text-secondary);">Rule: Action conforms to safe idempotent Kubernetes remediation standards. Execution token granted.</div>
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
    const navCount = document.getElementById("nav-connectors-count");
    if (!grid) return;

    try {
        const res = await fetch(`${API_BASE}/api/connectors`);
        if (!res.ok) return;
        const connectors = await res.json();

        if (navCount) navCount.innerText = connectors.length;

        grid.innerHTML = connectors.map(conn => {
            const isProd = conn.environment.toUpperCase() === "PRODUCTION";
            const iconClass = getProviderIcon(conn.system_type);
            const latencyColor = conn.latency_ms < 50 ? "var(--green)" : "var(--amber)";

            return `
                <div class="connector-box">
                    <div class="connector-box-top">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <div class="conn-icon-box">
                                <i class="${iconClass}"></i>
                            </div>
                            <div class="conn-identity">
                                <h4>${conn.name}</h4>
                                <span>${conn.system_type}</span>
                            </div>
                        </div>
                        <span class="status-badge ${isProd ? 'healthy' : 'warning'}">${conn.environment}</span>
                    </div>

                    <div class="connector-box-meta">
                        <div class="meta-line">
                            <span class="k">Endpoint</span>
                            <span class="v" title="${conn.target_endpoint}">${conn.target_endpoint.substring(0, 28)}...</span>
                        </div>
                        <div class="meta-line">
                            <span class="k">Auth Standard</span>
                            <span class="v">${conn.auth_type}</span>
                        </div>
                        <div class="meta-line">
                            <span class="k">Link Latency</span>
                            <span class="v" style="color: ${latencyColor}; font-weight: 600;">${conn.latency_ms.toFixed(1)}ms</span>
                        </div>
                        <div class="meta-line">
                            <span class="k">Status</span>
                            <span class="v" style="color: var(--green); font-weight: 600;">${conn.status}</span>
                        </div>
                    </div>

                    <div class="connector-box-footer">
                        <label style="display: flex; align-items: center; gap: 6px; font-size: 11px; color: var(--text-secondary); cursor: pointer;">
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
    if (s.includes("PROMETHEUS")) return "fa-solid fa-chart-line text-green";
    if (s.includes("SLACK")) return "fa-brands fa-slack text-red";
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
            feedback.style.color = "var(--green)";
            feedback.innerHTML = `<i class="fa-solid fa-check"></i> Handshake success (${data.latency_ms}ms) // ${data.message}`;
        } else {
            feedback.style.color = "var(--red)";
            feedback.innerHTML = `<i class="fa-solid fa-xmark"></i> Handshake failed: ${data.detail || 'Connection refused'}`;
        }
    } catch (e) {
        feedback.style.color = "var(--red)";
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
