"""
Data ingestion module.
Loads raw CSV sales data and performs schema validation.
"""

import pandas as pd
from pathlib import Path
from src.utils.logger import get_logger
from src.utils.config import config

log = get_logger("ingestion")

REQUIRED_COLUMNS = {"date", "product_id", "store_id", "sales_qty", "price"}


class DataIngestion:
    """Handles loading and basic validation of raw sales data."""

    def __init__(self, filepath: str = None):
        self.filepath = filepath or config.raw_data_path

    def load(self) -> pd.DataFrame:
        """Load CSV and validate schema.

        Returns:
            pd.DataFrame: Raw validated dataframe.

        Raises:
            FileNotFoundError: If the source file does not exist.
            ValueError: If required columns are missing.
        """
        path = Path(self.filepath)
        if not path.exists():
            log.error(f"Source file not found: {self.filepath}")
            raise FileNotFoundError(f"Data file missing: {self.filepath}")

        log.info(f"Loading data from {self.filepath}")
        df = pd.read_csv(path, parse_dates=["date"])

        self._validate_schema(df)
        log.info(f"Loaded {len(df):,} rows, {df.shape[1]} columns")
        return df

    def _validate_schema(self, df: pd.DataFrame) -> None:
        """Check all required columns are present."""
        missing = REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        log.info("Schema validation passed")

    def get_baseline_statistics(self, df: pd.DataFrame) -> dict:
        """Compute baseline statistics for drift detection later.

        These are stored during EDA and compared at inference time.
        """
        stats = {}
        numeric_cols = df.select_dtypes(include="number").columns
        for col in numeric_cols:
            stats[col] = {
                "mean": float(df[col].mean()),
                "std": float(df[col].std()),
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "q25": float(df[col].quantile(0.25)),
                "q75": float(df[col].quantile(0.75)),
            }
        log.info(f"Computed baseline statistics for {len(stats)} columns")
        return stats