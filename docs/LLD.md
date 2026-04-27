# Low-Level Design (LLD)
## API Endpoint Specifications

Base URL: `http://localhost:8000`
All requests: `Content-Type: application/json`

---

### POST /api/v1/predict

**Purpose**: Predict demand for a single product-store-date combination

**Request Body**
```json
{
  "product_id": "P004",
  "store_id": "S003",
  "forecast_date": "2024-08-20",
  "price": 90.0,
  "price_lag_7": 92.0,
  "sales_lag_1": 60.0,
  "sales_lag_7": 58.0,
  "sales_rolling_mean_7": 59.0,
  "discount": 0.1,
  "inventory_level": 1,
  "competitor_price": 88.0,
  "promotion": 1,
  "weather": "rainy",
  "seasonality": 2,
  "epidemic": 0
}
```

**Response 200 OK**
```json
{
  "product_id": "P004",
  "store_id": "S003",
  "forecast_date": "2024-08-20",
  "predicted_demand": 41.05,
  "model_version": "1",
  "inference_latency_ms": 6.8
}
```

**Errors**: `422` validation error, `500` model failure

---

### POST /api/v1/predict/batch

**Purpose**: Predict demand for up to 1000 combinations

**Request Body**
```json
{ "requests": [ { ...same as single predict... } ] }
```

**Response 200 OK**
```json
{
  "predictions": [ ...array of PredictionResponse... ],
  "batch_size": 5,
  "total_latency_ms": 34.2
}
```

---

### GET /health

**Purpose**: Liveness probe

**Response 200 OK**
```json
{
  "status": "ok",
  "timestamp": "2024-08-20T10:30:00Z",
  "uptime_seconds": 3600.0
}
```

---

### GET /ready

**Purpose**: Readiness probe — model loaded + MLflow reachable

**Response 200 OK**
```json
{
  "ready": true,
  "model_loaded": true,
  "mlflow_connected": true
}
```

---

### GET /api/v1/pipeline/status

**Purpose**: Pipeline run status for UI dashboard

**Response 200 OK**
```json
{
  "pipelines": [
    {
      "pipeline_name": "data_ingestion",
      "last_run_status": "success",
      "last_run_time": "2024-08-20T00:05:00",
      "rows_processed": 50000
    }
  ],
  "drift_detected": false,
  "drift_features": []
}
```

---

### GET /metrics

**Purpose**: Prometheus scrape endpoint

**Response**: Prometheus text format

---

## Module-Level Design

| Module | Class | Key Methods |
|---|---|---|
| `src/data/ingestion.py` | `DataIngestion` | `load()`, `get_baseline_statistics()` |
| `src/data/preprocessing.py` | `DataPreprocessor` | `run()`, `save()` |
| `src/data/feature_engineering.py` | `FeatureEngineer` | `run()`, `get_feature_columns()`, `save()` |
| `src/models/base_model.py` | `BaseModel` (ABC) | `train()`, `predict()`, `evaluate()` |
| `src/models/xgboost_model.py` | `XGBoostModel` | inherits BaseModel, MLflow autolog |
| `src/models/trainer.py` | `ModelTrainer` | `run()`, `promote_to_production()` |
| `src/monitoring/drift_detector.py` | `DriftDetector` | `detect()`, `should_retrain()` |
| `backend/services/inference_service.py` | `InferenceService` | `predict()`, `is_ready()` |

## Prometheus Metrics Exposed

| Metric | Type | Description |
|---|---|---|
| `demand_forecast_requests_total` | Counter | Total requests by endpoint and status |
| `demand_forecast_request_latency_seconds` | Histogram | Request latency buckets |
| `demand_forecast_prediction_value` | Gauge | Latest prediction per product/store |
| `demand_forecast_model_mae` | Gauge | Current model MAE |
| `demand_forecast_feature_drift_score` | Gauge | KS test score per feature |
| `demand_forecast_drift_alerts_total` | Counter | Total drift alerts triggered |
| `demand_forecast_pipeline_run_success` | Gauge | Pipeline health (1=ok, 0=failed) |
| `demand_forecast_retraining_triggered_total` | Counter | Retraining trigger count |