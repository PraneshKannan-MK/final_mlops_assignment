"""
Feature engineering module.

Adds:
- Temporal features
- Price features
- Lag features
- Rolling statistics
- Fourier seasonality
- Business-aware external features
"""

import pandas as pd
import numpy as np
from src.utils.logger import get_logger
from src.utils.config import config

log = get_logger("feature_engineering")


class FeatureEngineer:

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        log.info("Starting feature engineering")

        df = df.copy()
        df = self._temporal_features(df)
        df = self._price_features(df)
        df = self._lag_features(df)
        df = self._rolling_features(df)
        df = self._seasonality_features(df)
        df = self._external_features(df)

        # 🔥 CRITICAL FIX: enforce numeric types where possible
        df = self._ensure_numeric(df)

        log.info(f"Feature engineering complete. Total columns: {len(df.columns)}")
        return df

    # -------------------------
    # TEMPORAL
    # -------------------------
    def _temporal_features(self, df):
        df["year"] = df["date"].dt.year
        df["month"] = df["date"].dt.month
        df["day_of_week"] = df["date"].dt.dayofweek
        df["day_of_year"] = df["date"].dt.dayofyear
        df["week_of_year"] = df["date"].dt.isocalendar().week.astype(int)
        df["quarter"] = df["date"].dt.quarter
        df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
        df["is_month_start"] = df["date"].dt.is_month_start.astype(int)
        df["is_month_end"] = df["date"].dt.is_month_end.astype(int)
        return df

    # -------------------------
    # PRICE FEATURES
    # -------------------------
    def _price_features(self, df):
        df = df.sort_values(["product_id", "store_id", "date"])

        df["price_lag_7"] = df.groupby(["product_id", "store_id"])["price"].shift(7)
        df["price_pct_change"] = df.groupby(["product_id", "store_id"])["price"].pct_change()

        df["price_rolling_mean_7"] = (
            df.groupby(["product_id", "store_id"])["price"]
            .transform(lambda x: x.rolling(7, min_periods=1).mean())
        )
        return df

    # -------------------------
    # LAG FEATURES
    # -------------------------
    def _lag_features(self, df):
        grp = df.groupby(["product_id", "store_id"])["sales_qty"]

        for lag in [1, 7, 14, 28]:
            df[f"sales_lag_{lag}"] = grp.shift(lag)

        return df

    # -------------------------
    # ROLLING FEATURES
    # -------------------------
    def _rolling_features(self, df):
        grp = df.groupby(["product_id", "store_id"])["sales_qty"]

        for window in [7, 14, 28]:
            df[f"sales_rolling_mean_{window}"] = grp.transform(
                lambda x: x.rolling(window, min_periods=1).mean()
            )
            df[f"sales_rolling_std_{window}"] = grp.transform(
                lambda x: x.rolling(window, min_periods=1).std()
            )

        return df

    # -------------------------
    # FOURIER SEASONALITY
    # -------------------------
    def _seasonality_features(self, df):
        day_of_year = df["date"].dt.dayofyear

        for k in [1, 2, 3]:
            df[f"sin_{k}"] = np.sin(2 * np.pi * k * day_of_year / 365)
            df[f"cos_{k}"] = np.cos(2 * np.pi * k * day_of_year / 365)

        return df

    # -------------------------
    # BUSINESS FEATURES
    # -------------------------
    def _external_features(self, df):

        if "discount" in df.columns:
            df["discount_effect"] = df["price"] * (1 - df["discount"])

        if "inventory_level" in df.columns:
            df["low_stock_flag"] = (df["inventory_level"] < 10).astype(int)

        if "competitor_price" in df.columns:
            df["price_diff"] = df["price"] - df["competitor_price"]

        if "promotion" in df.columns:
            df["is_promo"] = df["promotion"].astype(int)

        if "weather" in df.columns:
            df["is_rainy"] = df["weather"].str.contains("Rain", case=False, na=False).astype(int)

        # 🔥 FIXED: seasonality conversion
        if "seasonality" in df.columns:
            df["seasonality_index"] = df["seasonality"].astype("category").cat.codes

        if "epidemic" in df.columns:
            df["epidemic_flag"] = df["epidemic"].astype(int)

        return df

    # -------------------------
    # 🔥 CRITICAL FIX FUNCTION
    # -------------------------
    def _ensure_numeric(self, df):
        """
        Ensures all model features are numeric.
        Prevents XGBoost crashes due to object dtype.
        """
        for col in df.columns:
            if df[col].dtype == "object":
                try:
                    df[col] = pd.to_numeric(df[col], errors="ignore")
                except Exception:
                    pass
        return df

    # -------------------------
    # FINAL FEATURE LIST
    # -------------------------
    def get_feature_columns(self):
        return [
            "year", "month", "day_of_week", "day_of_year", "week_of_year",
            "quarter", "is_weekend", "is_month_start", "is_month_end",

            "price", "price_lag_7", "price_pct_change", "price_rolling_mean_7",

            "sales_lag_1", "sales_lag_7", "sales_lag_14", "sales_lag_28",

            "sales_rolling_mean_7", "sales_rolling_mean_14", "sales_rolling_mean_28",
            "sales_rolling_std_7", "sales_rolling_std_14", "sales_rolling_std_28",

            "sin_1", "cos_1", "sin_2", "cos_2", "sin_3", "cos_3",

            "discount_effect",
            "low_stock_flag",
            "price_diff",
            "is_promo",
            "is_rainy",
            "seasonality_index",
            "epidemic_flag",
        ]

    def save(self, df: pd.DataFrame, path: str = None):
        out = path or config.feature_data_path
        df.to_csv(out, index=False)
        log.info(f"Saved features → {out}")