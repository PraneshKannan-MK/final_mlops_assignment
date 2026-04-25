"""
Pipeline status router.
GET /api/v1/pipeline/status — pipeline run statuses for UI dashboard.
"""

import json
import os
from fastapi import APIRouter
from backend.schemas.request_schemas import PipelineStatusResponse, PipelineRunInfo
from src.utils.logger import get_logger

log = get_logger("pipeline_router")
router = APIRouter()

STATUS_FILE = "data/processed/pipeline_status.json"
DRIFT_FILE = "data/processed/drift_results.json"


@router.get("/pipeline/status", response_model=PipelineStatusResponse)
def pipeline_status():
    """Return status of all data and ML pipelines."""
    pipelines = []

    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE) as f:
                raw = json.load(f)
            for name, info in raw.items():
                pipelines.append(PipelineRunInfo(
                    pipeline_name=name,
                    last_run_status=info.get("status", "unknown"),
                    last_run_time=info.get("run_time"),
                    rows_processed=info.get("rows_processed"),
                ))
        except Exception as e:
            log.error(f"Failed to read pipeline status: {e}")
    else:
        for name in ["data_ingestion", "feature_engineering", "model_training"]:
            pipelines.append(PipelineRunInfo(
                pipeline_name=name,
                last_run_status="never",
                last_run_time=None,
                rows_processed=None,
            ))

    drift_detected = False
    drift_features = []
    if os.path.exists(DRIFT_FILE):
        try:
            with open(DRIFT_FILE) as f:
                drift_results = json.load(f)
            drift_features = [f for f, r in drift_results.items() if r.get("is_drifted")]
            drift_detected = len(drift_features) > 0
        except Exception:
            pass

    return PipelineStatusResponse(
        pipelines=pipelines,
        drift_detected=drift_detected,
        drift_features=drift_features,
    )