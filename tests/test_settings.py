import pytest
from pydantic import ValidationError

from cartflow.settings import Settings


def test_environment_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CARTFLOW_ENVIRONMENT", "test")
    monkeypatch.setenv("CARTFLOW_SERVICE_NAME", "cartflow")
    monkeypatch.setenv("CARTFLOW_DEBUG", "True")

    settings = Settings()

    assert settings.environment == "test"
    assert settings.service_name == "cartflow"
    assert settings.debug is True


def test_environment_production_debug_false(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CARTFLOW_ENVIRONMENT", "production")
    monkeypatch.setenv("CARTFLOW_SERVICE_NAME", "cartflow")
    monkeypatch.setenv("CARTFLOW_DEBUG", "True")
    with pytest.raises(ValidationError):
        Settings()


def test_environment_no_env_provided(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "CARTFLOW_ENVIRONMENT",
        "CARTFLOW_SERVICE_NAME",
        "CARTFLOW_DEBUG",
    ):
        monkeypatch.delenv(name, raising=False)

    settings = Settings()

    assert settings.environment == "local"
    assert settings.service_name == "cartflow"
    assert settings.debug is False


def test_environment_debug_string_conversion(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CARTFLOW_ENVIRONMENT", "test")
    monkeypatch.setenv("CARTFLOW_SERVICE_NAME", "cartflow")
    monkeypatch.setenv("CARTFLOW_DEBUG", "true")

    settings = Settings()

    assert settings.environment == "test"
    assert settings.service_name == "cartflow"
    assert settings.debug is True


def test_environment_wrong_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CARTFLOW_ENVIRONMENT", "testovski")

    with pytest.raises(ValidationError):
        Settings()
