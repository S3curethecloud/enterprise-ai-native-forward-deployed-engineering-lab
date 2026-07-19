"""Fail-closed configuration for the local Phase 3 service foundation."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven settings with prohibited capabilities fixed off."""

    model_config = SettingsConfigDict(
        env_prefix="CBIDA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        frozen=True,
    )

    application_name: str = "Citation-Backed Incident Diagnostic Assistant"
    application_version: str = "0.1.0"
    environment: Literal["local", "test"] = "local"
    service_name: Literal["gateway", "runtime", "evidence"] = "gateway"
    host: str = "127.0.0.1"
    port: int = Field(default=8000, ge=1024, le=65535)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    external_model_enabled: Literal[False] = False
    enterprise_retrieval_enabled: Literal[False] = False
    tool_execution_enabled: Literal[False] = False
    infrastructure_mutation_enabled: Literal[False] = False
    cloud_deployment_enabled: Literal[False] = False
    production_deployment_enabled: Literal[False] = False


@lru_cache
def get_settings() -> Settings:
    """Return one immutable settings instance per local process."""

    return Settings()
