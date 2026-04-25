"""Unit tests for data preprocessing module."""

import pytest
import pandas as pd
import numpy as np
from src.data.preprocessing import DataPreprocessor


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"]),
        "product_id": ["P001", "P001", "P002", "P002"],
        "store_id": ["S001", "S001", "S001", "S001"],
        "sales_qty": [10.0, np.nan, 200.0, 15.0],
        "price": [29.99, 29.99, np.nan, 19.99],
    })


def test_preprocessor_runs_without_error(sample_df):
    result = DataPreprocessor().run(sample_df)
    assert result is not None and len(result) > 0


def test_missing_sales_qty_filled(sample_df):
    result = DataPreprocessor().run(sample_df)
    assert result["sales_qty"].isna().sum() == 0


def test_sales_qty_non_negative(sample_df):
    result = DataPreprocessor().run(sample_df)
    assert (result["sales_qty"] >= 0).all()


def test_outlier_bounds_stored(sample_df):
    pp = DataPreprocessor()
    pp.run(sample_df)
    assert "sales_qty" in pp.outlier_bounds
    assert pp.outlier_bounds["sales_qty"]["lower"] >= 0


def test_result_sorted_by_date(sample_df):
    result = DataPreprocessor().run(sample_df)
    for _, grp in result.groupby(["product_id", "store_id"]):
        assert grp["date"].is_monotonic_increasing