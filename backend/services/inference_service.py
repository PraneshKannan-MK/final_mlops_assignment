"""
Inference service.
Uses mlflow.xgboost.load_model to bypass MLflow pyfunc schema enforcement.
All Prometheus metrics defined here — single source, single registry.
"""

import time
import numpy as np
import pandas as pd
import mlflow
import mlflow.xgboost
from prometheus_client import Counter, Histogram, Gauge

from src.utils.config import config
from src.utils.logger import get_logger

log = get_logger("inference_service")


# ── Prometheus metrics ────────────────────────────────────────────────────────
# Defined once here — nowhere else. metrics_exporter.py imports from here.

REQUEST_COUNT = Counter(
    "demand_forecast_requests_total",
    "Total number of prediction requests",
    ["endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "demand_forecast_request_latency_seconds",
    "Prediction request latency in seconds",
    ["endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0],
)

PREDICTION_VALUE = Gauge(
    "demand_forecast_prediction_value",
    "Latest predicted demand value",
    ["product_id", "store_id"],
)

MODEL_MAE = Gauge("demand_forecast_model_mae", "Current model MAE")
MODEL_RMSE = Gauge("demand_forecast_model_rmse", "Current model RMSE")

DATA_ROWS_PROCESSED = Counter(
    "demand_forecast_data_rows_processed_total",
    "Total data rows processed by pipeline",
)

FEATURE_DRIFT_SCORE = Gauge(
    "demand_forecast_feature_drift_score",
    "KS test statistic for feature drift",
    ["feature_name"],
)

DRIFT_ALERT = Counter(
    "demand_forecast_drift_alerts_total",
    "Number of drift alerts triggered",
    ["feature_name"],
)

PIPELINE_RUN_STATUS = Gauge(
    "demand_forecast_pipeline_run_success",
    "1 if last pipeline run succeeded, 0 if failed",
    ["pipeline_name"],
)

RETRAINING_TRIGGERED = Counter(
    "demand_forecast_retraining_triggered_total",
    "Total number of retraining jobs triggered",
    ["trigger_reason"],
)


# ── Service ───────────────────────────────────────────────────────────────────

class InferenceService:

    def __init__(self):
        self.model = None
        self.model_version = "unknown"
        self._load_model()

    def _load_model(self) -> None:
        """
        Load XGBoost model directly via mlflow.xgboost.load_model.
        Bypasses MLflow pyfunc schema enforcement which blocks int64->int32.
        """
        try:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)

            client = mlflow.MlflowClient()
            versions = client.search_model_versions(f"name='{config.model_name}'")

            if not versions:
                raise RuntimeError(f"No versions found for model '{config.model_name}'")

            latest = sorted(versions, key=lambda x: int(x.version))[-1]
            self.model_version = latest.version

            model_uri = f"models:/{config.model_name}/{self.model_version}"
            self.model = mlflow.xgboost.load_model(model_uri)

            log.info(f"Loaded XGBoost model '{config.model_name}' v{self.model_version}")

        except Exception as e:
            log.error(f"Model loading failed: {e}")
            raise

    def predict(self, features: dict) -> tuple:
        start = time.time()
        try:
            # Extract identifiers before building model input
            product_id = str(features.get("product_id", "unknown"))
            store_id = str(features.get("store_id", "unknown"))

            # Remove non-model columns
            model_features = {
                k: v for k, v in features.items()
                if k not in ("product_id", "store_id")
            }

            df = pd.DataFrame([model_features])

            int_cols = [
                "year", "month", "day_of_week", "day_of_year", "week_of_year",
                "quarter", "is_weekend", "is_month_start", "is_month_end",
                "low_stock_flag", "is_promo", "is_rainy",
                "seasonality_index", "epidemic_flag",
            ]
            float_cols = [
                "price", "price_lag_7", "price_pct_change", "price_rolling_mean_7",
                "sales_lag_1", "sales_lag_7", "sales_lag_14", "sales_lag_28",
                "sales_rolling_mean_7", "sales_rolling_mean_14", "sales_rolling_mean_28",
                "sales_rolling_std_7", "sales_rolling_std_14", "sales_rolling_std_28",
                "sin_1", "cos_1", "sin_2", "cos_2", "sin_3", "cos_3",
                "discount_effect", "price_diff",
            ]

            for col in int_cols:
                if col in df.columns:
                    df[col] = df[col].astype(np.int64)

            for col in float_cols:
                if col in df.columns:
                    df[col] = df[col].astype(np.float64)

            pred = float(np.maximum(self.model.predict(df)[0], 0))
            latency_ms = (time.time() - start) * 1000

            REQUEST_COUNT.labels(endpoint="/predict", status="success").inc()
            REQUEST_LATENCY.labels(endpoint="/predict").observe(latency_ms / 1000)
            PREDICTION_VALUE.labels(
                product_id=product_id,
                store_id=store_id,
            ).set(pred)

            log.info(f"Prediction: {pred:.2f} | {latency_ms:.2f}ms")
            return pred, latency_ms

        except Exception as e:
            REQUEST_COUNT.labels(endpoint="/predict", status="error").inc()
            log.error(f"Prediction failed: {e}")
            raise
        
    def is_ready(self) -> bool:
        return self.model is not None


# ── Singleton ─────────────────────────────────────────────────────────────────

_service_instance: InferenceService = None


def get_inference_service() -> InferenceService:
    """FastAPI dependency injection — returns shared singleton."""
    global _service_instance
    if _service_instance is None:
        _service_instance = InferenceService()
    return _service_instance