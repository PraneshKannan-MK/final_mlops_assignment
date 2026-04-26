# Assisted by Chatgpt for the params
import pandas as pd
import mlflow

from src.models.xgboost_model import XGBoostModel
from src.data.feature_engineering import FeatureEngineer
from src.utils.logger import get_logger
from src.utils.config import config

log = get_logger("trainer")


class ModelTrainer:

    def __init__(self):
        self.feature_engineer = FeatureEngineer()

    def run(self, df: pd.DataFrame, params: dict = None) -> str:
        """Run full training pipeline with proper MLflow registry."""

        # 🔥 CRITICAL FIX — connect to MLflow server
        mlflow.set_tracking_uri(config.mlflow_tracking_uri or "http://localhost:5000")

        feature_cols = self.feature_engineer.get_feature_columns()
        target_col = "sales_qty"

        df_model = df[feature_cols + [target_col, "date", "product_id", "store_id"]].dropna()

        X = df_model[feature_cols]
        y = df_model[target_col]

        log.info(f"Training on {len(X):,} samples, {len(feature_cols)} features")

        with mlflow.start_run() as run:
            run_id = run.info.run_id

            # --- Log dataset info ---
            mlflow.log_param("n_samples", len(X))
            mlflow.log_param("n_features", len(feature_cols))

            # --- Train model ---
            model = XGBoostModel(params)
            log.info("Training model: xgboost")

            model.train(X, y)
            y_pred = model.predict(X)
            metrics = model.evaluate(X, y)

            # --- Log metrics ---
            mlflow.log_metrics({f"xgboost_{k}": v for k, v in metrics.items()})
            log.info(f"Model RMSE: {metrics['rmse']:.4f}")

            # --- Register model ---
            from mlflow.models.signature import infer_signature

            signature = infer_signature(X, model.predict(X))

            mlflow.xgboost.log_model(
                model.model,
                artifact_path="model",
                signature=signature,
                registered_model_name=config.model_name,  # MUST be "demand_forecaster"
            )

            log.info(f"Training complete. Run ID: {run_id}")
            log.info(f"Model registered as: {config.model_name}")

            return run_id