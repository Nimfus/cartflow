from typing import Annotated

from fastapi import APIRouter, Depends

from cartflow.dependencies import get_settings
from cartflow.settings import Settings

router = APIRouter()


@router.get("/health/live")
async def live(settings: Annotated[Settings, Depends(get_settings)]) -> dict[str, str]:
    return {"service": settings.service_name, "status": "ok"}


@router.get("/health/ready")
async def ready() -> dict[str, str]:
    return {"status": "ok"}
