╔═══════════════════════════════════════════════════════════════════════════════╗
║                    RETAIL DEMAND FORECASTING SYSTEM                           ║
║                         SYSTEM ARCHITECTURE                                   ║
╚═══════════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                              DATA LAYER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
  │  sales.csv  │    │  price.csv  │    │ calendar /  │    │  external   │
  │  (raw data) │    │             │    │  seasonal   │    │  factors    │
  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
         │                  │                  │                   │
         └──────────────────┴──────────────────┴───────────────────┘
                                        │
                                        ▼

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                           DATA PIPELINE LAYER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                        APACHE AIRFLOW DAG                               │
  │                   (Scheduled: Daily at midnight)                        │
  │                                                                         │
  │  ┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────┐  │
  │  │  Ingest  │───►│ Preprocess   │───►│   Feature    │───►│   DVC    │  │
  │  │   Data   │    │ Clean/Fill/  │    │  Engineering │    │   Push   │  │
  │  │          │    │ Outlier cap  │    │ Lag/Rolling/ │    │          │  │
  │  └──────────┘    └──────────────┘    │ Fourier/Time │    └──────────┘  │
  │                                      └──────────────┘                  │
  └─────────────────────────────────────────────────────────────────────────┘
         │                                                        │
         ▼                                                        ▼
  ┌─────────────┐                                       ┌─────────────────┐
  │  Baseline   │                                       │   DVC Remote    │
  │   Stats     │                                       │   (Versioned    │
  │  (JSON)     │                                       │    Artifacts)   │
  └─────────────┘                                       └─────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                           ML TRAINING LAYER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                         MODEL TRAINER                                   │
  │                                                                         │
  │   Features ──► TimeSeriesSplit CV ──► XGBoost ──► Evaluation           │
  │                  (5 folds)                          MAE/RMSE/MAPE       │
  │                                                          │              │
  │                                                          ▼              │
  │                                              ┌───────────────────────┐  │
  │                                              │    MLflow Tracking    │  │
  │                                              │  - Parameters         │  │
  │                                              │  - Metrics            │  │
  │                                              │  - Feature importance │  │
  │                                              │  - Model artifact     │  │
  │                                              └───────────┬───────────┘  │
  │                                                          │              │
  │                                                          ▼              │
  │                                              ┌───────────────────────┐  │
  │                                              │   MLflow Model        │  │
  │                                              │   Registry            │  │
  │                                              │   (Production stage)  │  │
  │                                              └───────────────────────┘  │
  └─────────────────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                         APPLICATION LAYER (DOCKER COMPOSE)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ┌───────────────────────┐              ┌───────────────────────────────────┐
  │   FRONTEND SERVICE    │              │        BACKEND SERVICE            │
  │   React + Recharts    │              │     FastAPI + Uvicorn             │
  │   Port: 3001          │◄────REST────►│     Port: 8000                    │
  │                       │    API       │                                   │
  │  Pages:               │              │  Endpoints:                       │
  │  - Forecast           │              │  POST /api/v1/predict             │
  │  - Pipeline Monitor   │              │  POST /api/v1/predict/batch       │
  │                       │              │  GET  /health                     │
  │  Components:          │              │  GET  /ready                      │
  │  - ForecastChart      │              │  GET  /api/v1/pipeline/status     │
  │  - MetricsDashboard   │              │  GET  /metrics                    │
  │  - PipelineVisualizer │              │                                   │
  └───────────────────────┘              └───────────────┬───────────────────┘
                                                         │
                                         ┌───────────────▼───────────────────┐
                                         │         MLFLOW SERVICE            │
                                         │     Model Registry + Tracking     │
                                         │     Port: 5000                    │
                                         │                                   │
                                         │  - Loads Production model         │
                                         │  - XGBoost direct inference       │
                                         │  - Version management             │
                                         └───────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                         MONITORING LAYER (DOCKER COMPOSE)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ┌───────────────────────┐    scrapes     ┌───────────────────────────────┐
  │   PROMETHEUS SERVICE  │◄───/metrics────│      FastAPI /metrics         │
  │   Port: 9090          │   every 15s    │      (generate_latest())      │
  │                       │                └───────────────────────────────┘
  │  Collects:            │
  │  - Request count      │    feeds       ┌───────────────────────────────┐
  │  - Latency histogram  │───────────────►│      GRAFANA SERVICE          │
  │  - Prediction values  │                │      Port: 3000               │
  │  - Drift scores       │                │                               │
  │  - Pipeline health    │                │  Dashboards:                  │
  │  - Retraining count   │                │  - Request rate               │
  └───────────────────────┘                │  - Latency over time          │
                                           │  - Prediction values          │
                                           │  - Error rate                 │
                                           │  - Drift alerts               │
                                           └───────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                              CI/CD LAYER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Git Push ──► GitHub Actions ──► pytest ──► dvc repro ──► docker build
                                    │
                                    ▼
                              DVC Pipeline DAG
                         ingest → preprocess → featurize → train

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                         BLOCK EXPLANATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BLOCK              TECHNOLOGY            PURPOSE
---------------------------------------------------------------------------
Frontend           React + Recharts      User interface, forecast input form,
                                         pipeline visualizer, live metrics
Backend            FastAPI + Uvicorn     REST API, prediction endpoint,
                                         health/readiness probes
Model Server       MLflow + XGBoost      Model registry, versioning, inference
Data Pipeline      Apache Airflow        Orchestrates daily ETL DAG
Versioning         DVC + Git LFS         Tracks data, models, code artifacts
Experiment Track   MLflow Tracking       Logs params, metrics, artifacts per run
Instrumentation    Prometheus Client     Exposes metrics at /metrics endpoint
Visualization      Grafana               NRT dashboards, alerting rules
Containerization   Docker Compose        5 isolated services, env parity
CI/CD              GitHub Actions        Auto test, DVC repro, Docker build
Drift Detection    SciPy KS Test         Compares live data vs training baseline