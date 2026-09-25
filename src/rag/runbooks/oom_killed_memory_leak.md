# SRE Runbook: OOMKilled Memory Leak Incident

## 1. Symptoms & Diagnostic Indicators
* **Kubernetes Reason**: `OOMKilled` (Exit Code 137).
* **Pod Status**: `CrashLoopBackOff` or rapid restart count increments.
* **Error Signature**: `Out of memory allocation failure`, `Process killed by kernel`, `MemoryLimitExceeded`.
* **Telemetry**: Memory usage metric `container_memory_working_set_bytes` constantly climbs with 100% linear slope without garbage collection drop.

## 2. Root Cause Analysis
1. Unbounded in-memory cache, unclosed file descriptors, or event listener leak.
2. Sudden load surge exceeding current Kubernetes pod resource limit.
3. Heap misconfiguration.

## 3. Allowed Remediation Actions
1. **Immediate Service Recovery (Restart)**: Restart pod to clear heap buffer and immediately restore traffic handling.
   ```bash
   kubectl rollout restart deployment/user-service -n production
   ```
2. **Increase Memory Limit Quota**: Patch pod spec with increased memory ceiling.
   ```bash
   kubectl set resources deployment/user-service -c=user-service --limits=memory=512Mi -n production
   ```

## 4. Verification Check
* Ensure pod status transitions to `RUNNING` with `0` restart increments over 60 seconds.
* Confirm `container_memory_usage_bytes` stays below 60% of the allocated ceiling.
