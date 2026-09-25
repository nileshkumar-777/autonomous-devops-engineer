# SRE Runbook: High Traffic Surge & CPU Saturation

## 1. Symptoms & Diagnostic Indicators
* **HTTP Status Codes**: 429 Too Many Requests, 503 Service Unavailable, 504 Gateway Timeout.
* **Error Signatures**: `Too many requests in pipeline`, `Thread pool queue full`, `CPU saturation > 85%`, `Connection timeout acquiring worker`.
* **Telemetry Anomalies**: Request volume surges 5x-10x, CPU saturation hits 85%-98%, P95 latency spikes to 2500ms+.
* **System Event**: Sudden flash crowd or traffic burst overwhelming current replica capacity.

## 2. Root Cause Analysis
1. Traffic spike or viral surge exceeding provisioned pod replica capacity.
2. Inadequate concurrency limit / thread pool exhaustion in web worker process.
3. Lack of auto-scaling triggers responding quickly enough to handle rapid request velocity.

## 3. Allowed Remediation Actions
1. **Horizontal Pod Autoscaling (Scale Deployment)**:
   Increase replica count proportionally to absorb request load across pods.
   ```bash
   kubectl scale deployment/<service-name> --replicas=5 -n production
   ```
2. **Rate Limiting & Traffic Shedding**:
   Enforce token-bucket rate limiting at ingress or gateway to shed excess requests with HTTP 429, shielding backend database pools.

## 4. Verification Check
* Verify CPU saturation drops back below 50%.
* Verify P95 latency normalizes below 200ms.
* Verify HTTP 2xx success rate returns to > 99.5%.
