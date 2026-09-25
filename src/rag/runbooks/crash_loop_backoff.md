# SRE Runbook: CrashLoopBackOff & Failed Readiness Probes

## 1. Symptoms & Diagnostic Indicators
* **Kubernetes Status**: `CrashLoopBackOff`, `Error`, `ContainerCannotRun`.
* **K8s Event**: `Readiness probe failed: HTTP probe failed with statuscode: 500`, `Back-off restarting failed container`.
* **Pod State**: Pod continually restarts, delaying deployment completion.

## 2. Root Cause Analysis
1. Missing environment variable or secrets (e.g. database password or dependent URL).
2. Service crashes during startup initialization (e.g., failed migrations or unhandled import error).
3. Readiness probe timeout too aggressive before warm-up completes.

## 3. Allowed Remediation Actions
1. **Rollback to Last Stable Deployment**:
   ```bash
   kubectl rollout undo deployment/order-service -n production
   ```
2. **Inspect Startup Logs**:
   ```bash
   kubectl logs deployment/order-service --previous -n production
   ```

## 4. Verification Check
* Inspect deployment status: `kubectl rollout status deployment/order-service -n production`.
* Confirm all replicas are `READY 1/1` and receiving traffic.
