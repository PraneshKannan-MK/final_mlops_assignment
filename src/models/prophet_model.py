"""
Prophet model implementation for demand forecasting.

Handles:
- Training with date-based data
- Prediction
- Save / Load
"""

import pandas as pd
import numpy as np
from prophet import Prophet
import joblib

from src.models.base_model import BaseModel
from src.utils.logger import get_logger

log = get_logger("prophet_model")


class ProphetModel(BaseModel):

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.model = None

    # -------------------------
    # TRAIN
    # -------------------------
    def train(self, X: pd.DataFrame, y: pd.Series) -> None:
        """
        Prophet expects:
        ds → date
        y  → target
        """

        if "date" not in X.columns:
            raise ValueError("Prophet requires 'date' column in input")

        df = X.copy()
        df["y"] = y.values

        df = df.rename(columns={"date": "ds"})

        log.info(f"Training Prophet on {len(df)} samples")

        self.model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False
        )

        self.model.fit(df[["ds", "y"]])

        self.is_trained = True

    # -------------------------
    # PREDICT
    # -------------------------
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_trained:
            raise RuntimeError("Model must be trained before prediction")

        if "date" not in X.columns:
            raise ValueError("Prophet requires 'date' column")

        df = X.rename(columns={"date": "ds"}).copy()

        forecast = self.model.predict(df[["ds"]])

        return forecast["yhat"].values

    # -------------------------
    # SAVE
    # -------------------------
    def save(self, path: str) -> None:
        if not self.is_trained:
            raise RuntimeError("Model not trained")

        joblib.dump(self.model, path)
        log.info(f"Prophet model saved → {path}")

    # -------------------------
    # LOAD
    # -------------------------
    def load(self, path: str) -> None:
        self.model = joblib.load(path)
        self.is_trained = True
        log.info(f"Prophet model loaded ← {path}")