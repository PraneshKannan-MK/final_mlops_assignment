"""
Inference Service
FINAL STABLE VERSION (DICT RETURN)
"""

import os
import time
import joblib
import numpy as np
import pandas as pd
import mlflow

from src.utils.logger import get_logger
from src.utils.config import config

# ✅ ADD THIS IMPORT (PROMETHEUS METRICS)
from src.monitoring.metrics_exporter import (
    REQUEST_COUNT, REQUEST_LATENCY, PREDICTION_VALUE
)

log = get_logger("inference_service")


class InferenceService:

    def __init__(self):
        self.model = None
        self.feature_columns = None
        self.model_version = None
        self._load_model()

    def _load_model(self):
        try:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
            client = mlflow.MlflowClient()

            versions = client.search_model_versions(
                f"name='{config.model_name}'"
            )

            if not versions:
                raise RuntimeError("No model found")

            prod = [v for v in versions if v.current_stage == "Production"]
            target = prod[0] if prod else versions[-1]

            self.model_version = target.version
            run_id = target.run_id

            local_dir = mlflow.artifacts.download_artifacts(
                run_id=run_id,
                artifact_path="model",
                dst_path="./tmp_model"
            )

            model_file = os.path.join(local_dir, "model.joblib")

            obj = joblib.load(model_file)

            # handle all formats
            if isinstance(obj, dict):
                self.model = obj.get("model")
                self.feature_columns = obj.get("features")

            elif isinstance(obj, tuple):
                self.model = obj[0]
                self.feature_columns = obj[1] if len(obj) > 1 else None

            else:
                self.model = obj
                self.feature_columns = None

            log.info(f"Model loaded (v{self.model_version})")

        except Exception as e:
            log.error(f"Model loading failed: {e}")
            raise

    def predict(self, features: dict):

        try:
            start = time.time()

            df = pd.DataFrame([features])

            # align features
            if self.feature_columns:
                missing = [c for c in self.feature_columns if c not in df.columns]

                for col in missing:
                    df[col] = 0

                df = df[self.feature_columns]

            df = df.apply(pd.to_numeric, errors="coerce").fillna(0)

            preds = self.model.predict(df)
            preds = np.maximum(preds, 0)

            latency = (time.time() - start) * 1000

            # ✅ ADD THESE 3 LINES (METRICS)
            REQUEST_COUNT.inc()
            REQUEST_LATENCY.observe(latency / 1000)
            PREDICTION_VALUE.observe(preds[0])

            return {
                "prediction": float(preds[0]),
                "latency_ms": round(latency, 2)
            }

        except Exception as e:
            log.error(f"Prediction failed: {e}")
            raise


_service = None


def get_inference_service():
    global _service
    if _service is None:
        _service = InferenceService()
    return _service