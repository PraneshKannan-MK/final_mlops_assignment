"""
Prepare raw retail dataset to match pipeline schema.

- Renames columns
- Chooses correct target (Demand)
- Keeps only required columns
- Outputs: data/raw/sales.csv
"""

import pandas as pd


def run():
    # Load raw dataset
    df = pd.read_csv("data/raw/retail_dataset.csv")

    # --- Rename columns to match pipeline ---
    df = df.rename(columns={
        "Date": "date",
        "Store ID": "store_id",
        "Product ID": "product_id",
        "Units Sold": "units_sold",
        "Price": "price",
        "Discount": "discount",
        "Inventory Level": "inventory_level",
        "Competitor Pricing": "competitor_price",
        "Weather Condition": "weather",
        "Promotion": "promotion",
        "Seasonality": "seasonality",
        "Epidemic": "epidemic",
        "Demand": "demand"
    })

    # --- TARGET DECISION ---
    # Use DEMAND as final target (not units_sold)
    df["sales_qty"] = df["demand"]

    # --- Keep only relevant columns ---
    df = df[[
        "date",
        "store_id",
        "product_id",
        "sales_qty",
        "price",
        "discount",
        "inventory_level",
        "competitor_price",
        "weather",
        "promotion",
        "seasonality",
        "epidemic"
    ]]

    # --- Type fixes ---
    df["date"] = pd.to_datetime(df["date"])
    df["store_id"] = df["store_id"].astype(str)
    df["product_id"] = df["product_id"].astype(str)

    # --- Save ---
    df.to_csv("data/raw/sales.csv", index=False)

    print(f"Saved cleaned dataset → data/raw/sales.csv | rows={len(df)}")


if __name__ == "__main__":
    run()