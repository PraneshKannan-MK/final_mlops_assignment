import pandas as pd
from src.data.feature_engineering import FeatureEngineer


def test_feature_engineering_runs():
    df = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=10),
        "store_id": ["S1"] * 10,
        "product_id": ["P1"] * 10,
        "sales_qty": range(10),
        "price": [10]*10,
        "discount": [0]*10,
        "inventory_level": [20]*10,
        "competitor_price": [11]*10,
        "weather": ["Sunny"]*10,
        "promotion": [0]*10,
        "seasonality": [1]*10,
        "epidemic": [0]*10
    })

    fe = FeatureEngineer()
    result = fe.run(df)

    assert len(result.columns) > len(df.columns)