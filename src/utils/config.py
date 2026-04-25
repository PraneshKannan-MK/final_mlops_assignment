"""
Application-wide configuration loaded from environment variables.
Never hardcode secrets — use .env at dev time, real env vars in containers.
"""

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    # Paths
    raw_data_path: str = field(default_factory=lambda: os.getenv("RAW_DATA_PATH", "data/raw/sales.csv"))
    processed_data_path: str = field(default_factory=lambda: os.getenv("PROCESSED_DATA_PATH", "data/processed/sales_clean.csv"))
    feature_data_path: str = field(default_factory=lambda: os.getenv("FEATURE_DATA_PATH", "data/features/sales_features.csv"))

    # MLflow
    mlflow_tracking_uri: str = field(default_factory=lambda: os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))
    mlflow_experiment_name: str = field(default_factory=lambda: os.getenv("MLFLOW_EXPERIMENT", "demand-forecasting"))

    # Model
    model_name: str = field(default_factory=lambda: os.getenv("MODEL_NAME", "demand_forecaster"))
    model_stage: str = field(default_factory=lambda: os.getenv("MODEL_STAGE", "Production"))

    # API
    api_host: str = field(default_factory=lambda: os.getenv("API_HOST", "0.0.0.0"))
    api_port: int = field(default_factory=lambda: int(os.getenv("API_PORT", "8000")))

    # Monitoring
    prometheus_port: int = field(default_factory=lambda: int(os.getenv("PROMETHEUS_PORT", "8001")))
    drift_threshold: float = field(default_factory=lambda: float(os.getenv("DRIFT_THRESHOLD", "0.05")))


# Singleton
config = Config()