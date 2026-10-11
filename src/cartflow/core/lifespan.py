from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from cartflow.settings import Settings


def create_lifespan(settings: Settings) -> Any:

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:

        yield

    return lifespan
