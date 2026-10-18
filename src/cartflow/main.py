from fastapi import FastAPI

from cartflow.api.health import router as health_router
from cartflow.core.lifespan import create_lifespan
from cartflow.settings import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings if settings is not None else Settings()

    app = FastAPI(
        title=resolved_settings.service_name, debug=resolved_settings.debug, lifespan=create_lifespan(resolved_settings)
    )
    app.state.settings = resolved_settings
    app.state.ready = False

    app.include_router(health_router)

    return app
