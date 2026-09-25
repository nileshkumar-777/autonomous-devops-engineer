# SRE Runbook: Database Connection Pool Exhausted

## 1. Symptoms & Diagnostic Indicators
* **HTTP Status Code**: 503 Service Unavailable or 500 Internal Server Error.
* **Error Signature**: `Database connection pool exhausted`, `timeout acquiring connection from pool`, `psycopg2.OperationalError: FATAL: too many connections`.
* **Latency Pattern**: Sharp exponential increase in p99 and p95 response time (> 5000ms).
* **Target Services**: Typically originates in `payment-service` or core transactional data pipelines.

## 2. Root Cause Analysis
1. High concurrent traffic exceeding maximum pool limit (`max_connections` or `pool_size`).
2. Long-running queries blocking worker threads without releasing connections back to pool.
3. Leaked unclosed database sessions in error handling paths.

## 3. Allowed Remediation Actions
1. **Rolling Restart**: Perform a rolling restart of the affected deployment to clear stuck connections and re-initialize the pool.
   ```bash
   kubectl rollout restart deployment/payment-service -n production
   ```
2. **Horizontal Scaling**: Scale replicas to distribute connection load if traffic demand is genuinely elevated.
   ```bash
   kubectl scale deployment/payment-service --replicas=4 -n production
   ```

## 4. Verification Check
* Inspect Prometheus metric: `http_requests_total{status="503"}` should drop to 0 within 30 seconds.
* Check pod health endpoint: `GET /health` must return `"db_connected": true` and `"status": "healthy"`.
