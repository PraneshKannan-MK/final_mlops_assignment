"""
XGBoost demand forecasting model.
Inherits from BaseModel and integrates with MLflow autolog.
"""

import numpy as np
import pandas as pd
import xgboost as xgb
import mlflow
import mlflow.xgboost
import joblib
from src.models.base_model import BaseModel
from src.utils.logger import get_logger

log = get_logger("xgboost_model")

DEFAULT_PARAMS = {
    "n_estimators": 500,
    "max_depth": 6,
    "learning_rate": 0.05,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "min_child_weight": 5,
    "reg_alpha": 0.1,
    "reg_lambda": 1.0,
    "objective": "reg:squarederror",
    "n_jobs": -1,
    "random_state": 42,
}


class XGBoostModel(BaseModel):
    """XGBoost gradient boosting model for demand forecasting."""

    def __init__(self, params: dict = None):
        merged = {**DEFAULT_PARAMS, **(params or {})}
        super().__init__(merged)
        self.feature_importances_: dict = {}

    def train(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        """Train XGBoost with MLflow autologging."""
        log.info(f"Training XGBoost with {len(X_train):,} samples")
        mlflow.xgboost.autolog(log_models=True, log_datasets=False)

        self.model = xgb.XGBRegressor(**self.params)
        self.model.fit(X_train, y_train, verbose=100)
        self.is_trained = True

        imp = self.model.get_booster().get_fscore()
        self.feature_importances_ = imp
        top5 = sorted(imp.items(), key=lambda x: -x[1])[:5]
        log.info(f"Top 5 features: {top5}")

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_trained:
            raise RuntimeError("Model is not trained")
        preds = self.model.predict(X)
        return np.maximum(preds, 0)  # demand cannot be negative

    def save(self, path: str) -> None:
        joblib.dump(self.model, path)
        log.info(f"Model saved to {path}")

    def load(self, path: str) -> None:
        self.model = joblib.load(path)
        self.is_trained = True
        log.info(f"Model loaded from {path}")