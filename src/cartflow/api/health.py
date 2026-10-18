from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status

from cartflow.dependencies import get_settings
from cartflow.settings import Settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
async def live(settings: Annotated[Settings, Depends(get_settings)]) -> dict[str, str]:
    return {"service": settings.service_name, "status": "ok"}


@router.get("/ready", responses={503: {"description": "Service is not ready"}})
async def ready(request: Request, response: Response) -> dict[str, str]:
    if not request.app.state.ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

        return {"status": "Service is not ready"}

    return {"status": "ok"}
