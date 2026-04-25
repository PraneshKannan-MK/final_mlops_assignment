# User Manual

## Setup
- Clone repo
- Install dependencies
- Run Docker

## Run Training
python -m src.pipeline.train_pipeline

## Start API
uvicorn backend.main:app --reload

## Make Prediction
POST /api/v1/predict

## View Metrics
- MLflow: localhost:5000
- Grafana: localhost:3000