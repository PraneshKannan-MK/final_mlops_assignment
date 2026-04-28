"""
Model Trainer
FINAL FIXED VERSION — handles datatype issues
"""

import os
import numpy as np
import pandas as pd
import joblib
import mlflow
from mlflow.tracking import MlflowClient
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error

from src.models.xgboost_model import XGBoostModel
from src.utils.logger import get_logger

log = get_logger("trainer")


class ModelTrainer:

    def __init__(self):
        self.model = None
        self.client = MlflowClient()
        mlflow.set_experiment("demand-forecasting")

    def _clean_features(self, df: pd.DataFrame):
        """
        🔥 CRITICAL FIX — remove invalid columns for XGBoost
        """

        drop_cols = []

        for col in df.columns:
            if df[col].dtype == "object":
                drop_cols.append(col)

            if str(df[col].dtype).startswith("datetime"):
                drop_cols.append(col)

        df = df.drop(columns=drop_cols)

        log.info(f"Dropped columns: {drop_cols}")

        return df

    def _split_data(self, df: pd.DataFrame):
        y = df["sales_qty"]
        X = df.drop(columns=["sales_qty"])

        # 🔥 FIX HERE
        X = self._clean_features(X)

        return train_test_split(X, y, test_size=0.2, random_state=42)

    def _evaluate(self, y_true, y_pred):
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))

        log.info(f"MAE: {mae:.4f}, RMSE: {rmse:.4f}")

        return {"mae": mae, "rmse": rmse}

    def run(self, df: pd.DataFrame):

        X_train, X_test, y_train, y_test = self._split_data(df)

        log.info(f"Training on {X_train.shape[0]} rows, {X_train.shape[1]} features")

        with mlflow.start_run() as run:

            run_id = run.info.run_id

            self.model = XGBoostModel()
            self.model.train(X_train, y_train)

            preds = self.model.predict(X_test)

            metrics = self._evaluate(y_test, preds)

            for k, v in metrics.items():
                mlflow.log_metric(k, v)

            # ✅ SAVE MODEL CORRECTLY
            model_dir = "artifacts/model"
            os.makedirs(model_dir, exist_ok=True)

            model_path = os.path.join(model_dir, "model.joblib")

            model_artifact = {
                "model": self.model.model,
                "features": list(X_train.columns)
            }

            joblib.dump(model_artifact, model_path)

            log.info(f"Model saved with {len(X_train.columns)} features")

            mlflow.log_artifact(model_path, artifact_path="model")

            model_name = "demand_forecaster"
            model_uri = f"runs:/{run_id}/model"

            result = mlflow.register_model(model_uri, model_name)

            log.info(f"Registered model version: {result.version}")

            return run_id

    def promote_to_production(self, run_id: str):

        model_name = "demand_forecaster"

        versions = self.client.search_model_versions(f"name='{model_name}'")

        latest = sorted(versions, key=lambda x: int(x.version))[-1]

        self.client.transition_model_version_stage(
            name=model_name,
            version=latest.version,
            stage="Production"
        )

        log.info(f"Model v{latest.version} promoted to Production")