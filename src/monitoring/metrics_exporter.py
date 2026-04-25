"""
metrics_exporter.py
Re-exports all Prometheus metrics from inference_service.
Import from here in drift_detector.py and anywhere else that needs metrics.
Do NOT define any Counter/Gauge/Histogram in this file.
"""

from backend.services.inference_service import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
    PREDICTION_VALUE,
    MODEL_MAE,
    MODEL_RMSE,
    DATA_ROWS_PROCESSED,
    FEATURE_DRIFT_SCORE,
    DRIFT_ALERT,
    PIPELINE_RUN_STATUS,
    RETRAINING_TRIGGERED,
)

__all__ = [
    "REQUEST_COUNT",
    "REQUEST_LATENCY",
    "PREDICTION_VALUE",
    "MODEL_MAE",
    "MODEL_RMSE",
    "DATA_ROWS_PROCESSED",
    "FEATURE_DRIFT_SCORE",
    "DRIFT_ALERT",
    "PIPELINE_RUN_STATUS",
    "RETRAINING_TRIGGERED",
]