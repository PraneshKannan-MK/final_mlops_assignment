"""
Airflow DAG: demand_forecast_pipeline
"""

from datetime import datetime, timedelta
import subprocess
import json
import os

from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "mlops",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

STATUS_FILE = "/app/data/processed/pipeline_status.json"


def _write_status(stage, status):
    data = {}
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE) as f:
            data = json.load(f)

    data[stage] = {
        "status": status,
        "time": datetime.utcnow().isoformat()
    }

    os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)

    with open(STATUS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def run_cmd(cmd, stage):
    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = "/app"   # 🔥 CRITICAL FIX

        subprocess.run(
            cmd,
            check=True,
            cwd="/app",
            env=env
        )
        _write_status(stage, "success")

    except Exception as e:
        _write_status(stage, "failed")
        raise


def ingest():
    run_cmd(["python", "-m", "src.data.ingestion"], "ingestion")


def preprocess():
    run_cmd(["python", "-m", "src.data.preprocessing"], "preprocessing")


def feature_engineer():
    run_cmd(["python", "-m", "src.data.feature_engineering"], "feature_engineering")


def train():
    run_cmd(["python", "-m", "src.pipeline.train_pipeline"], "training")


def dvc_push():
    run_cmd(["dvc", "push"], "dvc")


with DAG(
    dag_id="demand_forecast_pipeline",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule="@daily",   # 🔥 updated (no deprecation warning)
    catchup=False,
) as dag:

    t1 = PythonOperator(task_id="ingest", python_callable=ingest)
    t2 = PythonOperator(task_id="preprocess", python_callable=preprocess)
    t3 = PythonOperator(task_id="feature_engineer", python_callable=feature_engineer)
    t4 = PythonOperator(task_id="train", python_callable=train)
    t5 = PythonOperator(task_id="dvc_push", python_callable=dvc_push)

    t1 >> t2 >> t3 >> t4 >> t5