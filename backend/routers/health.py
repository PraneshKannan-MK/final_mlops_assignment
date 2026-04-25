"""
Health check endpoints.
GET /health  — liveness probe
GET /ready   — readiness probe
"""

import time
from datetime import datetime, timezone
from fastapi import APIRouter
from backend.schemas.request_schemas import HealthResponse, ReadyResponse
from src.utils.logger import get_logger

log = get_logger("health_router")
router = APIRouter()
_start_time = time.time()


@router.get("/health", response_model=HealthResponse)
def health():
    """Liveness probe — 200 if service is alive."""
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc).isoformat(),
        uptime_seconds=time.time() - _start_time,
    )


@router.get("/ready", response_model=ReadyResponse)
def ready():
    """Readiness probe — checks model load and MLflow connectivity."""
    import mlflow
    from src.utils.config import config

    model_loaded = False
    mlflow_connected = False

    try:
        mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        mlflow.search_experiments()
        mlflow_connected = True
    except Exception as e:
        log.warning(f"MLflow not reachable: {e}")

    try:
        from backend.services.inference_service import get_inference_service
        service = get_inference_service()
        model_loaded = service.is_ready()
    except Exception as e:
        log.warning(f"Model not loaded: {e}")

    return ReadyResponse(
        ready=model_loaded and mlflow_connected,
        model_loaded=model_loaded,
        mlflow_connected=mlflow_connected,
    )