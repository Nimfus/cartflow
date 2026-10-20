from collections.abc import AsyncIterator
from http.client import HTTPException
from typing import Annotated

from fastapi import Depends
from fastapi.testclient import TestClient

from cartflow.main import create_app
from cartflow.settings import Environment, Settings


def test_dependency_is_cached_within_request() -> None:
    app = create_app(Settings(environment=Environment.test))

    events: list[tuple[str, object]] = []

    async def acquire_probe() -> AsyncIterator[object]:
        resource = object()

        events.append(("open", resource))

        try:
            yield resource
        finally:
            events.append(("close", resource))

    @app.get("/__test__/scope", include_in_schema=False)
    async def check_scope(
        left: Annotated[object, Depends(acquire_probe)],
        right: Annotated[object, Depends(acquire_probe)],
    ) -> dict[str, bool]:
        return {"same": left is right}

    with TestClient(app) as client:
        first = client.get("/__test__/scope")
        second = client.get("/__test__/scope")

        assert first.json() == {"same": True}
        assert second.json() == {"same": True}

    assert [kind for kind, _ in events] == ["open", "close", "open", "close"]

    assert events[0][1] is events[1][1]
    assert events[2][1] is events[3][1]

    assert events[0][1] is not events[2][1]


def test_dependency_cleanup_after_handler_failure() -> None:
    app = create_app(Settings(environment=Environment.test))

    events: list[str] = []

    async def acquire_probe() -> AsyncIterator[object]:
        events.append("open")

        try:
            yield object()
        finally:
            events.append("close")

        @app.get("/__test__/failure", include_in_schema=False)
        async def failing_endpoint(
            resource: Annotated[object, Depends(acquire_probe)],
        ) -> None:
            raise HTTPException(status_code=503, detail="Injection failure")

        with TestClient(app) as client:
            resp = client.get("/__test__/failure")

            assert resp.status_code == 503

        assert events == ["open", "close"]
