# Retail Demand Forecasting System

AI-driven demand forecasting for retail using MLOps best practices.

## Quick Start

### Prerequisites
- Python 3.11
- Docker Desktop
- Node.js 20+

### Run locally (without Docker)
```bash
# Backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm start
```

### Run with Docker
```bash
docker-compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3001 |
| Backend API | http://localhost:8000/docs |
| MLflow | http://localhost:5000 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |

## Project Structure
├── airflow/          # Airflow DAGs for data pipeline
├── backend/          # FastAPI REST API
├── data/             # Raw, processed, feature data
├── docker/           # Dockerfiles + nginx config
├── docs/             # HLD, LLD, test plan, user manual
├── frontend/         # React dashboard
├── mlops/            # DVC pipeline config
├── monitoring/       # Prometheus + Grafana config
├── src/              # Core ML modules
├── tests/            # Unit tests
├── docker-compose.yml
├── MLproject
└── requirements.txt

## Documentation
- [Architecture Diagram](docs/architecture_diagram.md)
- [High-Level Design](docs/HLD.md)
- [Low-Level Design](docs/LLD.md)
- [Test Plan](docs/test_plan.md)
- [User Manual](docs/user_manual.md)

## Tech Stack
| Layer | Tool |
|---|---|
| Model | XGBoost |
| Pipeline | Apache Airflow |
| Versioning | DVC + Git |
| Experiment Tracking | MLflow |
| Backend | FastAPI |
| Frontend | React |
| Monitoring | Prometheus + Grafana |
| Packaging | Docker Compose |