import os
import zipfile
import time
import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report, roc_auc_score
from src.ml.log_parser import LogParser
from src.ml.feature_extractor import FeatureExtractor

DATASET_ZIP_PATH = os.path.join(os.path.dirname(__file__), "../../datasets/BGL.log.zip")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

def load_bgl_sample(max_normal: int = 15000, max_anomaly: int = 3000):
    """
    Stream BGL.log directly from zip to collect a balanced sample
    without loading the multi-hundred MB file entirely into memory.
    """
    print(f"[*] Reading BGL dataset from {DATASET_ZIP_PATH}...")
    normal_logs = []
    anomaly_logs = []

    with zipfile.ZipFile(DATASET_ZIP_PATH, "r") as z:
        with z.open("BGL.log") as f:
            for line_bytes in f:
                line_str = line_bytes.decode("utf-8", errors="ignore")
                parsed = LogParser.parse_bgl_line(line_str)
                if not parsed:
                    continue

                if parsed["is_anomaly_ground_truth"]:
                    if len(anomaly_logs) < max_anomaly:
                        anomaly_logs.append(parsed)
                else:
                    if len(normal_logs) < max_normal:
                        normal_logs.append(parsed)

                if len(normal_logs) >= max_normal and len(anomaly_logs) >= max_anomaly:
                    break

    print(f"[+] Loaded {len(normal_logs)} normal logs and {len(anomaly_logs)} anomaly logs.")
    return normal_logs, anomaly_logs

def train_and_evaluate():
    start_time = time.time()
    normal_logs, anomaly_logs = load_bgl_sample(max_normal=15000, max_anomaly=3000)

    all_logs = normal_logs + anomaly_logs
    # Ground truth labels: 1 for normal, -1 for anomaly (standard Isolation Forest convention)
    y_true = np.array([1 if not l["is_anomaly_ground_truth"] else -1 for l in all_logs])

    print("[*] Extracting features with TF-IDF and SRE metrics...")
    extractor = FeatureExtractor(max_features=250)
    X = extractor.fit_transform(all_logs)
    print(f"[+] Feature matrix shape: {X.shape}")

    # Isolation Forest setup
    contamination = len(anomaly_logs) / len(all_logs)
    print(f"[*] Training Isolation Forest (contamination={contamination:.3f})...")
    clf = IsolationForest(
        n_estimators=100,
        contamination=contamination,
        random_state=42,
        n_jobs=-1,
    )
    clf.fit(X)

    # Predict: 1 for inliers (normal), -1 for outliers (anomalies)
    y_pred = clf.predict(X)
    scores = -clf.decision_function(X)  # Higher score = more anomalous

    print("\n" + "=" * 60)
    print("Isolation Forest Model Evaluation on BGL Ground Truth:")
    print("=" * 60)
    # Map to 0 (normal) and 1 (anomaly) for classification report
    y_true_binary = (y_true == -1).astype(int)
    y_pred_binary = (y_pred == -1).astype(int)

    print(classification_report(y_true_binary, y_pred_binary, target_names=["Normal", "Anomaly"]))
    roc_auc = roc_auc_score(y_true_binary, scores)
    print(f"ROC-AUC Score: {roc_auc:.4f}")
    print(f"Training completed in {time.time() - start_time:.2f} seconds.")

    # Save artifacts
    os.makedirs(MODELS_DIR, exist_ok=True)
    model_path = os.path.join(MODELS_DIR, "isolation_forest.joblib")
    extractor_path = os.path.join(MODELS_DIR, "feature_extractor.joblib")

    joblib.dump(clf, model_path)
    joblib.dump(extractor, extractor_path)
    print(f"[+] Saved model to {model_path}")
    print(f"[+] Saved feature extractor to {extractor_path}")

if __name__ == "__main__":
    train_and_evaluate()
