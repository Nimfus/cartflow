import asyncio
from typing import Annotated

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from pydantic import ValidationError

from cartflow.dependencies import get_settings
from cartflow.main import create_app
from cartflow.settings import Environment, Settings


def settings_for(name: str, debug: bool = False) -> Settings:
    return Settings(environment=Environment.test, service_name=name, debug=debug)


def test_app_factory_uses_injected_settings() -> None:
    settings = settings_for("cartflow-test", debug=True)

    app = create_app(settings)

    assert app.title == "cartflow-test"
    assert app.debug is True
    assert app.state.settings is settings
    assert app.state.ready is False


def test_independent_apps_and_dependency_resolution() -> None:
    app_a = create_app(settings_for("cartflow-A"))
    app_b = create_app(settings_for("cartflow-B"))

    async def show_name(settings: Annotated[Settings, Depends(get_settings)]) -> dict[str, str]:
        return {"service": settings.service_name}

    app_a.add_api_route("/__test__/settings", show_name)
    app_b.add_api_route("/__test__/settings", show_name)

    assert app_a is not app_b
    assert app_a.state.settings is not app_b.state.settings

    with TestClient(app_a) as client_a:
        assert client_a.get("/__test__/settings").json() == {
            "service": "cartflow-A",
        }

        assert app_b.state.ready is False

        with TestClient(app_b) as client_b:
            assert client_b.get("/__test__/settings").json() == {
                "service": "cartflow-B",
            }

            assert app_a.state.ready is True
            assert app_b.state.ready is True

        assert app_a.state.ready is True
        assert app_b.state.ready is False

    assert app_a.state.ready is False


def test_health_lifespan_contract() -> None:
    app = create_app(settings_for("health-test"))

    assert app.state.ready is False

    # Without the context manager, lifespan is not executed.
    client_without_lifespan = TestClient(app)

    assert client_without_lifespan.get("/health/ready").status_code == 503

    assert client_without_lifespan.get("/health/live").status_code == 200

    with TestClient(app) as client:
        live = client.get("/health/live")
        ready = client.get("/health/ready")

        assert live.status_code == 200
        assert live.json() == {"service": "health-test", "status": "ok"}

        assert ready.status_code == 200
        assert ready.json() == {"status": "ok"}

    assert app.state.ready is False


def test_bad_production_settings_fail_fast() -> None:
    with pytest.raises(
        ValidationError,
        match="production environment with debug on",
    ):
        Settings(
            environment=Environment.production,
            debug=True,
        )

    settings = Settings(
        environment=Environment.production,
        debug=False,
    )

    assert settings.debug is False


def test_unexpected_lifespan_exit_clears_ready() -> None:
    app = create_app(settings_for("failure-test"))

    async def interrupted() -> None:
        async with app.router.lifespan_context(app):
            assert app.state.ready is True

            raise RuntimeError("injected interruption")

    with pytest.raises(
        RuntimeError,
        match="injected interruption",
    ):
        asyncio.run(interrupted())

    assert app.state.ready is False


def test_factory_resolves_settings_when_none_given(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CARTFLOW_ENVIRONMENT", "test")
    monkeypatch.setenv(
        "CARTFLOW_SERVICE_NAME",
        "cartflow-from-env",
    )
    monkeypatch.setenv("CARTFLOW_DEBUG", "false")

    app = create_app()

    assert app.title == "cartflow-from-env"
    assert app.state.settings.service_name == "cartflow-from-env"


def test_invalid_environment_prevents_app_construction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "CARTFLOW_ENVIRONMENT",
        "production",
    )
    monkeypatch.setenv("CARTFLOW_DEBUG", "true")

    with pytest.raises(
        ValidationError,
        match="production environment with debug on",
    ):
        create_app()
