import numpy as np
import scipy.sparse as sp
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Dict, Tuple, Any

class FeatureExtractor:
    """
    Transforms parsed log records into numerical feature vectors
    combining TF-IDF semantic embeddings and domain SRE features.
    """

    SEVERITY_MAP = {
        "INFO": 0,
        "DEBUG": 0,
        "NOTICE": 0,
        "WARN": 1,
        "WARNING": 1,
        "ERROR": 2,
        "SEVERE": 2,
        "FATAL": 3,
        "CRITICAL": 3,
        "FAILURE": 3,
    }

    CRITICAL_KEYWORDS = {"fail", "fatal", "error", "timeout", "kill", "exception", "abort", "corrupt", "panic", "oom"}

    def __init__(self, max_features: int = 200):
        self.max_features = max_features
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            token_pattern=r"(?u)\b\w+\b|<[A-Z]+>",
            ngram_range=(1, 2),
            lowercase=True,
        )
        self.is_fitted = False

    def _extract_statistical_features(self, logs: List[Dict]) -> np.ndarray:
        """Extract domain features: severity rank, token length, critical keyword flag."""
        features = []
        for log in logs:
            level = str(log.get("level", "INFO")).upper()
            sev_score = self.SEVERITY_MAP.get(level, 1)

            cleaned = str(log.get("cleaned_message", ""))
            tokens = cleaned.lower().split()
            msg_len = len(tokens)

            has_crit = 1.0 if any(k in cleaned.lower() for k in self.CRITICAL_KEYWORDS) else 0.0

            features.append([sev_score, msg_len, has_crit])

        return np.array(features, dtype=np.float32)

    def fit(self, logs: List[Dict]):
        """Fit the TF-IDF vectorizer on training log messages."""
        corpus = [log.get("cleaned_message", "") for log in logs]
        self.vectorizer.fit(corpus)
        self.is_fitted = True
        return self

    def transform(self, logs: List[Dict]) -> sp.csr_matrix:
        """Transform log list into combined sparse feature matrix."""
        if not self.is_fitted:
            raise ValueError("FeatureExtractor must be fitted before calling transform().")

        corpus = [log.get("cleaned_message", "") for log in logs]
        tfidf_features = self.vectorizer.transform(corpus)
        stat_features = self._extract_statistical_features(logs)

        # Horizontally stack TF-IDF and statistical features
        combined = sp.hstack([tfidf_features, sp.csr_matrix(stat_features)], format="csr")
        return combined

    def fit_transform(self, logs: List[Dict]) -> sp.csr_matrix:
        """Fit and transform in a single pass."""
        self.fit(logs)
        return self.transform(logs)
