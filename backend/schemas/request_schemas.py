"""
Pydantic I/O schemas for all API endpoints.
Interface specification from the Low-Level Design document.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional
from datetime import date as date_type


# ── Prediction ────────────────────────────────────────────────────────────────

class PredictionRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    product_id: str = Field(..., examples=["P001"])
    store_id: str = Field(..., examples=["S001"])
    forecast_date: str = Field(..., examples=["2024-03-15"])
    price: float = Field(..., gt=0, examples=[29.99])

    # Optional lag/rolling fields
    price_lag_7: Optional[float] = None
    sales_lag_1: Optional[float] = None
    sales_lag_7: Optional[float] = None
    sales_rolling_mean_7: Optional[float] = None

    # Optional contextual fields
    discount: Optional[float] = Field(default=0.0)
    inventory_level: Optional[int] = Field(default=1)
    competitor_price: Optional[float] = None
    promotion: Optional[int] = Field(default=0)
    weather: Optional[str] = Field(default="sunny")
    seasonality: Optional[int] = Field(default=1)
    epidemic: Optional[int] = Field(default=0)

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Price must be positive")
        return v

    @field_validator("forecast_date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        try:
            from datetime import datetime
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("forecast_date must be in YYYY-MM-DD format")
        return v


class PredictionResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    product_id: str
    store_id: str
    forecast_date: str
    predicted_demand: float
    model_version: str
    inference_latency_ms: float


class BatchPredictionRequest(BaseModel):
    requests: List[PredictionRequest] = Field(..., min_length=1, max_length=1000)


class BatchPredictionResponse(BaseModel):
    predictions: List[PredictionResponse]
    batch_size: int
    total_latency_ms: float


# ── Health ────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    uptime_seconds: float


class ReadyResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    ready: bool
    model_loaded: bool
    mlflow_connected: bool


# ── Pipeline ──────────────────────────────────────────────────────────────────

class PipelineRunInfo(BaseModel):
    pipeline_name: str
    last_run_status: str
    last_run_time: Optional[str] = None
    rows_processed: Optional[int] = None


class PipelineStatusResponse(BaseModel):
    pipelines: List[PipelineRunInfo]
    drift_detected: bool
    drift_features: List[str]