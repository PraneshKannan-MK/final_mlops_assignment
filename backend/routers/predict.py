"""
Prediction router.
POST /api/v1/predict        — single prediction
POST /api/v1/predict/batch  — batch predictions
"""

import time
import numpy as np
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException

from backend.schemas.request_schemas import (
    PredictionRequest, PredictionResponse,
    BatchPredictionRequest, BatchPredictionResponse,
)
from backend.services.inference_service import InferenceService, get_inference_service
from src.utils.logger import get_logger

log = get_logger("predict_router")
router = APIRouter()


def _build_features(req: PredictionRequest) -> dict:
    d = datetime.strptime(req.forecast_date, "%Y-%m-%d").date()
    day_of_year = d.timetuple().tm_yday

    is_rainy = 1 if (req.weather or "").lower() == "rainy" else 0
    is_promo = int(req.promotion or 0)
    discount = float(req.discount or 0.0)
    competitor_price = float(req.competitor_price or req.price)
    inventory_level = int(req.inventory_level or 1)
    seasonality = int(req.seasonality or 1)
    epidemic = int(req.epidemic or 0)

    return {
        # ADD THESE TWO LINES
        "product_id": req.product_id,
        "store_id": req.store_id,
        # Temporal
        "year": d.year,
        "month": d.month,
        "day_of_week": d.weekday(),
        "day_of_year": day_of_year,
        "week_of_year": d.isocalendar()[1],
        "quarter": (d.month - 1) // 3 + 1,
        "is_weekend": int(d.weekday() >= 5),
        "is_month_start": int(d.day == 1),
        "is_month_end": int(d.day >= 28),
        "price": float(req.price),
        "price_lag_7": float(req.price_lag_7 or req.price),
        "price_pct_change": 0.0,
        "price_rolling_mean_7": float(req.price),
        "sales_lag_1": float(req.sales_lag_1 or 0.0),
        "sales_lag_7": float(req.sales_lag_7 or 0.0),
        "sales_lag_14": 0.0,
        "sales_lag_28": 0.0,
        "sales_rolling_mean_7": float(req.sales_rolling_mean_7 or 0.0),
        "sales_rolling_mean_14": 0.0,
        "sales_rolling_mean_28": 0.0,
        "sales_rolling_std_7": 0.0,
        "sales_rolling_std_14": 0.0,
        "sales_rolling_std_28": 0.0,
        "sin_1": float(np.sin(2 * np.pi * 1 * day_of_year / 365)),
        "cos_1": float(np.cos(2 * np.pi * 1 * day_of_year / 365)),
        "sin_2": float(np.sin(2 * np.pi * 2 * day_of_year / 365)),
        "cos_2": float(np.cos(2 * np.pi * 2 * day_of_year / 365)),
        "sin_3": float(np.sin(2 * np.pi * 3 * day_of_year / 365)),
        "cos_3": float(np.cos(2 * np.pi * 3 * day_of_year / 365)),
        "discount_effect": float(req.price * discount),
        "low_stock_flag": int(inventory_level < 2),
        "price_diff": float(req.price - competitor_price),
        "is_promo": is_promo,
        "is_rainy": is_rainy,
        "seasonality_index": seasonality,
        "epidemic_flag": epidemic,
    }


@router.post("/predict", response_model=PredictionResponse)
def predict(
    request: PredictionRequest,
    service: InferenceService = Depends(get_inference_service),
):
    """Predict demand for a single product-store-date combination."""
    try:
        features = _build_features(request)
        prediction, latency_ms = service.predict(features)
        return PredictionResponse(
            product_id=request.product_id,
            store_id=request.store_id,
            forecast_date=request.forecast_date,
            predicted_demand=prediction,
            model_version=service.model_version,
            inference_latency_ms=latency_ms,
        )
    except Exception as e:
        log.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict/batch", response_model=BatchPredictionResponse)
def predict_batch(
    request: BatchPredictionRequest,
    service: InferenceService = Depends(get_inference_service),
):
    """Predict demand for a batch of product-store-date combinations."""
    start = time.time()
    predictions = []
    for req in request.requests:
        features = _build_features(req)
        pred, lat = service.predict(features)
        predictions.append(PredictionResponse(
            product_id=req.product_id,
            store_id=req.store_id,
            forecast_date=req.forecast_date,
            predicted_demand=pred,
            model_version=service.model_version,
            inference_latency_ms=lat,
        ))
    return BatchPredictionResponse(
        predictions=predictions,
        batch_size=len(predictions),
        total_latency_ms=(time.time() - start) * 1000,
    )