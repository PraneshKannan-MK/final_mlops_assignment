# High-Level Design (HLD)
## Retail Demand Forecasting System

### 1. Problem Statement
Predict product-level retail demand based on seasonal patterns and price variations
to enable better inventory planning by minimizing stockouts and overstock situations.

### 2. Success Metrics
| Type | Metric | Target |
|---|---|---|
| ML | MAE | < 15 units |
| ML | MAPE | < 20% |
| Business | Inference latency | < 200ms |
| Business | API uptime | > 99% |
| Business | Error rate | < 5% |

### 3. Design Principles
- **Loose coupling**: React frontend and FastAPI backend are independent Docker
  services connected only via configurable REST API calls
- **Reproducibility**: Every experiment reproducible via Git commit hash + MLflow run ID
- **Automation**: All pipeline stages automated via Airflow DAGs and DVC
- **Observability**: Prometheus exports metrics, Grafana visualizes in NRT

### 4. System Architecture
See architecture_diagram.md for full diagram.

### 5. Technology Choices & Rationale

| Layer | Choice | Rationale |
|---|---|---|
| Model | XGBoost | Strong baseline for tabular time-series, fast inference |
| Pipeline | Apache Airflow | DAG-based scheduling, visual pipeline console |
| Versioning | DVC + Git LFS | Tracks data and model artifacts alongside code |
| Experiment Tracking | MLflow | Unified params/metrics/artifacts/registry |
| Backend | FastAPI | Async, auto-generates OpenAPI docs, Pydantic validation |
| Frontend | React + Recharts | Component-based, responsive, lightweight |
| Monitoring | Prometheus + Grafana | Industry standard, NRT scraping, alert rules |
| Packaging | Docker Compose | 5 isolated services, environment parity |

### 6. Data Flow

Airflow triggers daily at midnight
Raw sales.csv ingested → schema validated → baseline stats computed
Preprocessing: missing values filled, outliers capped via IQR
Feature engineering: temporal + price + lag + rolling + Fourier features
DVC pushes versioned artifacts to remote
Model training: TimeSeriesSplit CV → MLflow logs all experiments
Best model promoted to Production stage in MLflow registry
FastAPI loads Production model at startup via mlflow.xgboost.load_model
POST /api/v1/predict → feature dict → XGBoost prediction → response
Prometheus scrapes /metrics every 15s → Grafana displays NRT


### 7. Drift Detection & Retraining
- KS test compares live inference data against training baseline statistics
- Alert triggered when 3+ features drift beyond p < 0.05 threshold
- Prometheus counter increments on each drift alert
- Grafana panel shows drift score per feature in NRT

### 8. Security
- All config via environment variables, never hardcoded
- .env excluded from Git
- CORS restricted to known frontend origins
- No cloud services used — fully on-prem