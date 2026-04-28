"""
End-to-end training pipeline.
Orchestrates preprocessing, feature engineering, model training, MLflow logging.
Run with: python -m src.pipeline.train_pipeline
"""

import os
import pandas as pd
import mlflow

from src.data.preprocessing import DataPreprocessor
from src.data.feature_engineering import FeatureEngineer
from src.models.trainer import ModelTrainer
from src.utils.logger import get_logger

log = get_logger("train_pipeline")


def run():
    log.info("Starting training pipeline")

    # Read MLflow URI from environment — set to Docker container when running locally
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    mlflow.set_tracking_uri(tracking_uri)
    log.info(f"MLflow tracking URI: {tracking_uri}")

    # Step 1 — Load raw data
    df = pd.read_csv("data/raw/sales.csv", parse_dates=["date"])
    log.info(f"Loaded data: {df.shape}")

    # Step 2 — Preprocessing
    preprocessor = DataPreprocessor()
    df_clean = preprocessor.run(df)
    log.info(f"After preprocessing: {df_clean.shape}")

    # Step 3 — Feature Engineering
    fe = FeatureEngineer()
    df_features = fe.run(df_clean)
    log.info(f"After feature engineering: {df_features.shape}")

    # Save features for DVC tracking
    os.makedirs("data/features", exist_ok=True)
    df_features.to_csv("data/features/sales_features.csv", index=False)
    log.info("Saved features to data/features/sales_features.csv")

    # Step 4 — Train model and log to MLflow
    trainer = ModelTrainer()
    run_id = trainer.run(df_features)

    # Step 5 — Promote to Production
    trainer.promote_to_production(run_id)

    log.info(f"Training completed. MLflow run_id={run_id}")
    log.info(f"Model registered as Production in MLflow")
    log.info(f"View at: {tracking_uri}/#/models")

    return run_id


if __name__ == "__main__":
    run()