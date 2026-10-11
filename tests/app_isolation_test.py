from fastapi.testclient import TestClient

from cartflow.main import create_app
from cartflow.settings import Environment, Settings


def test_settings_are_isolated_between_apps() -> None:
    app_a = create_app(
        Settings(
            environment=Environment.test,
            service_name="cartflow-a",
        )
    )

    app_b = create_app(
        Settings(
            environment=Environment.test,
            service_name="cartflow-b",
        )
    )

    assert app_a is not app_b
    assert app_a.state.settings is not app_b.state.settings

    with TestClient(app_a) as client_a:
        response_a = client_a.get("/health/live")

    with TestClient(app_b) as client_b:
        response_b = client_b.get("/health/live")

    assert response_a.status_code == 200
    assert response_b.status_code == 200
