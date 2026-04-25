"""
FastAPI backend entry point.
/metrics uses generate_latest() — reads same global registry
that inference_service.py writes to.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from backend.routers import predict, health, pipeline
from src.utils.logger import get_logger

log = get_logger("backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Backend starting up...")
    yield
    log.info("Backend shutting down...")


app = FastAPI(
    title="Demand Forecasting API",
    description="AI-driven retail demand forecasting service",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/metrics")
def metrics():
    """Prometheus scrape endpoint."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


app.include_router(predict.router, prefix="/api/v1", tags=["Prediction"])
app.include_router(health.router, tags=["Health"])
app.include_router(pipeline.router, prefix="/api/v1", tags=["Pipeline"])


@app.get("/")
def root():
    return {"service": "Demand Forecasting API", "status": "running"}