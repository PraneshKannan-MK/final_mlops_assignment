"""API endpoint tests using FastAPI TestClient."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock


@pytest.fixture
def mock_service():
    service = MagicMock()
    service.predict.return_value = (42.5, 12.3)
    service.model_version = "1"
    service.is_ready.return_value = True
    return service


@pytest.fixture
def client(mock_service):
    from backend.main import app
    from backend.services.inference_service import get_inference_service
    app.dependency_overrides[get_inference_service] = lambda: mock_service
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_health_returns_200(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_predict_valid_request(client):
    r = client.post("/api/v1/predict", json={
        "product_id": "P001", "store_id": "S001",
        "date": "2024-03-15", "price": 29.99,
    })
    assert r.status_code == 200
    data = r.json()
    assert data["predicted_demand"] == 42.5
    assert "model_version" in data
    assert "inference_latency_ms" in data


def test_predict_rejects_negative_price(client):
    r = client.post("/api/v1/predict", json={
        "product_id": "P001", "store_id": "S001",
        "date": "2024-03-15", "price": -5.0,
    })
    assert r.status_code == 422


def test_predict_rejects_missing_fields(client):
    r = client.post("/api/v1/predict", json={"product_id": "P001"})
    assert r.status_code == 422


def test_pipeline_status_shape(client):
    r = client.get("/api/v1/pipeline/status")
    assert r.status_code == 200
    data = r.json()
    assert "pipelines" in data
    assert "drift_detected" in data