"""
Data preprocessing module.
Handles missing values, outliers, type casting, and data cleaning.
"""

import pandas as pd
import numpy as np
from src.utils.logger import get_logger
from src.utils.config import config

log = get_logger("preprocessing")


class DataPreprocessor:
    """Cleans and prepares raw sales data for feature engineering."""

    def __init__(self):
        self.outlier_bounds: dict = {}

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        """Run full preprocessing pipeline.

        Args:
            df: Raw sales dataframe.

        Returns:
            Cleaned dataframe ready for feature engineering.
        """
        log.info("Starting preprocessing pipeline")
        df = df.copy()
        df = self._cast_types(df)
        df = self._handle_missing(df)
        df = self._remove_outliers(df)
        df = self._sort(df)
        log.info(f"Preprocessing complete. Rows remaining: {len(df):,}")
        return df

    def _cast_types(self, df: pd.DataFrame) -> pd.DataFrame:
        df["date"] = pd.to_datetime(df["date"])
        df["product_id"] = df["product_id"].astype(str)
        df["store_id"] = df["store_id"].astype(str)
        df["sales_qty"] = pd.to_numeric(df["sales_qty"], errors="coerce")
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        log.debug("Type casting complete")
        return df

    def _handle_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        initial = len(df)
        # Forward-fill missing sales quantities within each product-store group
        df["sales_qty"] = (
            df.groupby(["product_id", "store_id"])["sales_qty"]
            .transform(lambda x: x.ffill().bfill())
        )
        # Fill remaining with 0 (truly no data)
        df["sales_qty"] = df["sales_qty"].fillna(0)
        df["price"] = (
            df.groupby("product_id")["price"]
            .transform(lambda x: x.ffill().bfill())
        )
        dropped = initial - len(df.dropna(subset=["date"]))
        log.info(f"Missing value handling: {dropped} rows dropped for null dates")
        return df.dropna(subset=["date"])

    def _remove_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """IQR-based outlier capping for sales_qty."""
        q1 = df["sales_qty"].quantile(0.25)
        q3 = df["sales_qty"].quantile(0.75)
        iqr = q3 - q1
        lower = max(0.0, q1 - 1.5 * iqr)
        upper = q3 + 1.5 * iqr
        self.outlier_bounds = {"sales_qty": {"lower": lower, "upper": upper}}
        df["sales_qty"] = df["sales_qty"].clip(lower=lower, upper=upper)
        log.info(f"Outlier capping: sales_qty clipped to [{lower:.2f}, {upper:.2f}]")
        return df

    def _sort(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.sort_values(["product_id", "store_id", "date"]).reset_index(drop=True)

    def save(self, df: pd.DataFrame, path: str = None) -> None:
        out = path or config.processed_data_path
        df.to_csv(out, index=False)
        log.info(f"Saved processed data to {out}")