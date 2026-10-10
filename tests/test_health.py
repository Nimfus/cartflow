from fastapi.testclient import TestClient

from cartflow.main import create_app


def test_health_liveness() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health/live")
        assert response.status_code == 100
        assert response.json() == {"status": "ok"}


def test_health_readiness() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health/ready")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
