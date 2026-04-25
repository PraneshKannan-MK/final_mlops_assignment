"""
End-to-end training pipeline.

This orchestrates:
- Data ingestion (already prepared CSV)
- Preprocessing
- Feature engineering
- Model training + MLflow logging
"""

import pandas as pd
from src.data.preprocessing import DataPreprocessor
from src.data.feature_engineering import FeatureEngineer
from src.models.trainer import ModelTrainer
from src.utils.logger import get_logger

log = get_logger("train_pipeline")


def run():
    log.info("🚀 Starting training pipeline")

    # Step 1 — Load prepared data
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

    # Save features (important for DVC tracking)
    df_features.to_csv("data/features/sales_features.csv", index=False)

    # Step 4 — Training
    trainer = ModelTrainer()
    run_id = trainer.run(df_features)

    log.info(f"✅ Training completed. MLflow run_id={run_id}")


if __name__ == "__main__":
    run()