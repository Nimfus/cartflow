from enum import StrEnum
from typing import Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    local = "local"
    test = "test"
    production = "production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CARTFLOW_",
        env_file=".env",
        extra="ignore",
    )

    environment: Environment = Environment.local
    service_name: str = "cartflow"
    debug: bool = False

    @model_validator(mode="after")
    def validate_production_settings(self) -> Self:
        env = self.environment
        if env is Environment.production and self.debug:
            raise ValueError("production environment with debug on is not allowed")
        return self
