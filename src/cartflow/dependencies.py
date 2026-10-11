from typing import cast

from fastapi import Request

from cartflow.settings import Settings


def get_settings(request: Request) -> Settings:
    return cast(Settings, request.app.state.settings)
