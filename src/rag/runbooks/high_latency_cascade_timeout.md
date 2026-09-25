# SRE Runbook: High Latency Cascading Timeout

## 1. Symptoms & Diagnostic Indicators
* **HTTP Status Code**: 502 Bad Gateway or 504 Gateway Timeout.
* **Error Signature**: `Downstream timeout calling payment-service`, `RequestError: ReadTimeout`, `Connection reset by peer`.
* **Telemetry Anomaly**: `order-service` latency climbs to 4000ms+ because it waits for `payment-service` before responding.
* **System Event**: Cascade failure where frontend orders fail because payment backend is degraded.

## 2. Root Cause Analysis
1. Downstream dependent service (`payment-service`) is experiencing high latency or resource starvation.
2. Missing or overly generous client timeout configuration in `order-service`.
3. Lack of circuit breaker or graceful degradation fallback.

## 3. Allowed Remediation Actions
1. **Scale Downstream Service**: Increase replicas of `payment-service` to absorb query spikes.
   ```bash
   kubectl scale deployment/payment-service --replicas=3 -n production
   ```
2. **Restart Degraded Dependency**: Trigger rolling restart on the bottleneck service.
   ```bash
   kubectl rollout restart deployment/payment-service -n production
   ```

## 4. Verification Check
* Monitor `order-service` HTTP 201 Created rates.
* Confirm `order-service` p95 response time drops under 500ms.
