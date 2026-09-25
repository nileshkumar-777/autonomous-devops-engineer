import os
import joblib
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator
from src.ml.log_parser import LogParser

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODELS_DIR, "isolation_forest.joblib")
EXTRACTOR_PATH = os.path.join(MODELS_DIR, "feature_extractor.joblib")

app = FastAPI(
    title="AutoSRE ML Anomaly Detection Service",
    description="Unsupervised Isolation Forest log anomaly detector trained on real-world system telemetry.",
    version="1.0.0",
)

Instrumentator().instrument(app).expose(app)

# Load model weights on startup
clf = None
extractor = None

def load_artifacts():
    global clf, extractor
    if os.path.exists(MODEL_PATH) and os.path.exists(EXTRACTOR_PATH):
        clf = joblib.load(MODEL_PATH)
        extractor = joblib.load(EXTRACTOR_PATH)
    else:
        raise RuntimeError(f"Model artifacts not found in {MODELS_DIR}. Run train_model.py first.")

load_artifacts()

class LogInferenceRequest(BaseModel):
    log_line: str
    service_name: Optional[str] = "generic"

class BatchLogInferenceRequest(BaseModel):
    log_lines: List[str]
    service_name: Optional[str] = "generic"

def classify_parsed_log(parsed: Dict) -> Dict:
    X = extractor.transform([parsed])
    pred = clf.predict(X)[0]  # 1: normal, -1: anomaly
    raw_score = float(-clf.decision_function(X)[0])  # higher = more anomalous

    is_anomaly = (pred == -1) or (parsed.get("level") in ["ERROR", "FATAL", "CRITICAL"])

    # Determine severity
    if raw_score > 0.15 or parsed.get("level") in ["FATAL", "CRITICAL"]:
        severity = "CRITICAL"
    elif raw_score > 0.05 or is_anomaly:
        severity = "HIGH"
    elif parsed.get("level") in ["WARN", "WARNING"]:
        severity = "WARNING"
    else:
        severity = "NORMAL"

    return {
        "is_anomaly": is_anomaly,
        "severity": severity,
        "anomaly_score": round(raw_score, 4),
        "level": parsed.get("level", "INFO"),
        "component": parsed.get("component", "unknown"),
        "raw_message": parsed.get("raw_message", ""),
        "cleaned_message": parsed.get("cleaned_message", ""),
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ml-anomaly-detector",
        "model_loaded": clf is not None,
        "model_type": "IsolationForest",
        "features": extractor.max_features if extractor else 0,
    }

@app.post("/api/v1/predict")
def predict_single_log(request: LogInferenceRequest):
    parsed = LogParser.parse_microservice_line(request.log_line)
    result = classify_parsed_log(parsed)
    result["service_name"] = request.service_name
    return result

@app.post("/api/v1/predict/batch")
def predict_batch_logs(request: BatchLogInferenceRequest):
    if not request.log_lines:
        raise HTTPException(status_code=400, detail="Log lines list cannot be empty")

    parsed_list = [LogParser.parse_microservice_line(l) for l in request.log_lines]
    classified = [classify_parsed_log(p) for p in parsed_list]

    anomalies = [c for c in classified if c["is_anomaly"]]
    anomaly_rate = len(anomalies) / len(classified)

    return {
        "service_name": request.service_name,
        "total_logs": len(classified),
        "anomaly_count": len(anomalies),
        "anomaly_rate": round(anomaly_rate, 4),
        "system_status": "ANOMALOUS" if anomaly_rate > 0.05 else "HEALTHY",
        "anomalous_events": anomalies,
    }
