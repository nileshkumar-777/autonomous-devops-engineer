import re
from typing import Dict, List, Optional

class LogParser:
    """
    Parses unstructured log streams into structured dictionaries,
    normalizing dynamic tokens (hex addresses, numbers, IPs) into generic placeholders.
    Supports BGL supercomputer logs, standard syslogs, and microservice log formats.
    """

    # Regex patterns for variable token masking (Drain log abstraction)
    IP_REGEX = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
    HEX_REGEX = re.compile(r"\b0x[0-9a-fA-F]+\b")
    UUID_REGEX = re.compile(r"\b[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}\b")
    NUM_REGEX = re.compile(r"\b\d+\b")

    # Regex to parse standard BGL log lines:
    # Example: APPREAD 1117869872 2005.06.04 R23-M1-N8-I:J18-U11 2005-06-04-00.24.32.398284 R23-M1-N8-I:J18-U11 RAS APP FATAL ciod: failed to read
    BGL_REGEX = re.compile(
        r"^(?P<label>\S+)\s+(?P<timestamp>\d+)\s+(?P<date>\S+)\s+(?P<node>\S+)\s+(?P<datetime>\S+)\s+(?P<subnode>\S+)\s+(?P<system>\S+)\s+(?P<component>\S+)\s+(?P<level>\S+)\s+(?P<message>.*)$"
    )

    # Standard Microservice log line:
    # Example: 2026-09-25 18:05:40 [ERROR] [payment-service] Database connection pool exhausted
    MICROSERVICE_REGEX = re.compile(
        r"^(?P<datetime>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+\[(?P<level>\w+)\]\s+\[(?P<component>[^\]]+)\]\s+(?P<message>.*)$"
    )

    @classmethod
    def mask_tokens(cls, message: str) -> str:
        """Replace dynamic entities with generic masks for semantic clustering."""
        msg = cls.IP_REGEX.sub("<IP>", message)
        msg = cls.HEX_REGEX.sub("<HEX>", msg)
        msg = cls.UUID_REGEX.sub("<UUID>", msg)
        msg = cls.NUM_REGEX.sub("<NUM>", msg)
        return msg

    @classmethod
    def parse_bgl_line(cls, line: str) -> Optional[Dict]:
        """Parse a single raw line from the BGL dataset."""
        line = line.strip()
        if not line:
            return None

        match = cls.BGL_REGEX.match(line)
        if not match:
            # Fallback for irregular lines
            parts = line.split(maxsplit=9)
            if len(parts) >= 10:
                label = parts[0]
                return {
                    "is_anomaly_ground_truth": (label != "-"),
                    "label": label,
                    "timestamp": parts[1],
                    "node": parts[3],
                    "component": parts[7],
                    "level": parts[8],
                    "raw_message": parts[9],
                    "cleaned_message": cls.mask_tokens(parts[9]),
                }
            return None

        data = match.groupdict()
        is_anomaly = data["label"] != "-"
        return {
            "is_anomaly_ground_truth": is_anomaly,
            "label": data["label"],
            "timestamp": data["timestamp"],
            "node": data["node"],
            "component": data["component"],
            "level": data["level"],
            "raw_message": data["message"],
            "cleaned_message": cls.mask_tokens(data["message"]),
        }

    @classmethod
    def parse_microservice_line(cls, line: str) -> Dict:
        """Parse standard microservice output log lines."""
        line = line.strip()
        match = cls.MICROSERVICE_REGEX.match(line)
        if match:
            d = match.groupdict()
            level = d["level"].upper()
            is_anomaly = level in ["ERROR", "FATAL", "CRITICAL"]
            return {
                "is_anomaly_ground_truth": is_anomaly,
                "label": level,
                "timestamp": d["datetime"],
                "node": "k8s-pod",
                "component": d["component"],
                "level": level,
                "raw_message": d["message"],
                "cleaned_message": cls.mask_tokens(d["message"]),
            }

        # Generic fallback
        level = "INFO"
        if any(w in line.upper() for w in ["ERROR", "FATAL", "EXCEPTION", "FAIL", "TIMEOUT"]):
            level = "ERROR"

        return {
            "is_anomaly_ground_truth": (level == "ERROR"),
            "label": level,
            "timestamp": "",
            "node": "k8s-pod",
            "component": "generic",
            "level": level,
            "raw_message": line,
            "cleaned_message": cls.mask_tokens(line),
        }
