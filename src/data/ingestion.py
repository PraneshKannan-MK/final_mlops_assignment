import os
import pandas as pd
from loguru import logger

RAW_DATA_PATH = "/app/data/raw/sales.csv"  
PROCESSED_DIR = "/app/data/processed"
OUTPUT_PATH = os.path.join(PROCESSED_DIR, "ingested_data.csv")


def ingest_data():
    logger.info("Starting ingestion step...")

    if not os.path.exists(RAW_DATA_PATH):
        raise FileNotFoundError(f"Raw data not found at {RAW_DATA_PATH}")

    df = pd.read_csv(RAW_DATA_PATH)
    logger.info(f"Loaded raw data with shape: {df.shape}")

    if df.empty:
        raise ValueError("Input dataset is empty")

    os.makedirs(PROCESSED_DIR, exist_ok=True)

    df.to_csv(OUTPUT_PATH, index=False)
    logger.info(f"Ingested data saved to {OUTPUT_PATH}")

    return OUTPUT_PATH


def main():
    logger.info("Ingestion started")

    try:
        output = ingest_data()
        logger.success(f"Ingestion completed successfully → {output}")

    except Exception as e:
        logger.exception(f"Ingestion failed: {e}")
        raise


if __name__ == "__main__":
    main()