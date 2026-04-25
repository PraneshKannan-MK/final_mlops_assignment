"""
Abstract base class for all demand forecasting models.
Enforces a consistent interface across XGBoost, Prophet, etc.
"""

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from src.utils.logger import get_logger

log = get_logger("base_model")


class BaseModel(ABC):
    def __init__(self, params: dict = None):
        self.params = params or {}
        self.model = None
        self.is_trained = False

    @abstractmethod
    def train(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        pass

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        pass

    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
        """Compute evaluation metrics including BUSINESS metrics."""
        if not self.is_trained:
            raise RuntimeError("Model must be trained before evaluation")

        y_pred = self.predict(X_test)

        # --- Standard Metrics ---
        mae = float(np.mean(np.abs(y_test.values - y_pred)))
        rmse = float(np.sqrt(np.mean((y_test.values - y_pred) ** 2)))

        mask = y_test.values != 0
        mape = float(
            np.mean(
                np.abs((y_test.values[mask] - y_pred[mask]) / y_test.values[mask])
            ) * 100
        )

        metrics = {
            "mae": mae,
            "rmse": rmse,
            "mape": mape,
        }

        # --- BUSINESS METRICS ---
        business = self._business_metrics(y_test.values, y_pred)
        metrics.update(business)

        log.info(
            f"Eval — MAE: {mae:.4f}, RMSE: {rmse:.4f}, MAPE: {mape:.2f}% | "
            f"Total Cost: {business['total_cost']:.4f}"
        )

        return metrics

    def _business_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> dict:
        """
        Business-aware evaluation:
        Penalizes stockouts more heavily than overstock.
        """
        overstock = np.maximum(y_pred - y_true, 0)
        stockout = np.maximum(y_true - y_pred, 0)

        # You can tune these weights later (important for viva)
        overstock_cost = np.mean(overstock * 2)
        stockout_cost = np.mean(stockout * 5)

        return {
            "overstock_cost": float(overstock_cost),
            "stockout_cost": float(stockout_cost),
            "total_cost": float(overstock_cost + stockout_cost),
        }

    @abstractmethod
    def save(self, path: str) -> None:
        pass

    @abstractmethod
    def load(self, path: str) -> None:
        pass