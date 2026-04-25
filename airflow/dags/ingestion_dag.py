"""
Airflow DAG: demand_forecast_ingestion
Daily pipeline: ingest → preprocess → feature engineer → DVC push
"""

from datetime import datetime, timedelta
import json
import os
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "mlops-team",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

STATUS_FILE = "data/processed/pipeline_status.json"


def _write_status(pipeline_name: str, status: str, rows: int = None):
    existing = {}
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE) as f:
            existing = json.load(f)
    existing[pipeline_name] = {
        "status": status,
        "run_time": datetime.utcnow().isoformat(),
        "rows_processed": rows,
    }
    os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
    with open(STATUS_FILE, "w") as f:
        json.dump(existing, f, indent=2)


def ingest_data(**kwargs):
    from src.data.ingestion import DataIngestion
    ingestion = DataIngestion()
    df = ingestion.load()
    stats = ingestion.get_baseline_statistics(df)
    os.makedirs("data/processed", exist_ok=True)
    with open("data/processed/baseline_stats.json", "w") as f:
        json.dump(stats, f, indent=2)
    df.to_csv("data/processed/raw_validated.csv", index=False)
    _write_status("data_ingestion", "success", len(df))
    kwargs["ti"].xcom_push(key="row_count", value=len(df))


def preprocess_data(**kwargs):
    import pandas as pd
    from src.data.preprocessing import DataPreprocessor
    df = pd.read_csv("data/processed/raw_validated.csv", parse_dates=["date"])
    preprocessor = DataPreprocessor()
    df_clean = preprocessor.run(df)
    preprocessor.save(df_clean)
    _write_status("preprocessing", "success", len(df_clean))


def engineer_features(**kwargs):
    import pandas as pd
    from src.data.feature_engineering import FeatureEngineer
    df = pd.read_csv("data/processed/sales_clean.csv", parse_dates=["date"])
    engineer = FeatureEngineer()
    df_features = engineer.run(df)
    engineer.save(df_features)
    _write_status("feature_engineering", "success", len(df_features))


def dvc_push(**kwargs):
    import subprocess
    result = subprocess.run(["dvc", "push"], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"DVC push failed: {result.stderr}")
    _write_status("dvc_push", "success")


with DAG(
    dag_id="demand_forecast_ingestion",
    default_args=default_args,
    description="Daily data ingestion and feature engineering",
    schedule_interval="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["demand-forecasting", "mlops"],
) as dag:
    t1 = PythonOperator(task_id="ingest_data", python_callable=ingest_data)
    t2 = PythonOperator(task_id="preprocess_data", python_callable=preprocess_data)
    t3 = PythonOperator(task_id="engineer_features", python_callable=engineer_features)
    t4 = PythonOperator(task_id="dvc_push", python_callable=dvc_push)
    t1 >> t2 >> t3 >> t4