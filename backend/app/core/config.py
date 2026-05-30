"""Application configuration loaded from environment variables.

Centralizing settings here (and injecting them) keeps modules free of direct
``os.environ`` access — supporting the Dependency Inversion principle.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- App ---
    app_name: str = "FinSight"
    environment: Literal["dev", "staging", "prod"] = "dev"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:5173"]

    # --- Datastores ---
    database_url: str = Field(
        default="postgresql+asyncpg://finsight:finsight@localhost:5432/finsight",
        description="Async SQLAlchemy/asyncpg DSN for the application tables.",
    )
    # LangGraph's PostgresSaver/Store uses a sync psycopg DSN.
    checkpoint_database_url: str = Field(
        default="postgresql://finsight:finsight@localhost:5432/finsight",
        description="Sync DSN used by LangGraph PostgresSaver/PostgresStore.",
    )
    redis_url: str = "redis://localhost:6379/0"

    # --- LLM / embeddings (Google Gemini free tier via AI Studio) ---
    llm_provider: Literal["google"] = "google"
    google_api_key: str | None = None
    llm_model: str = "gemini-2.0-flash"
    embedding_model: str = "models/text-embedding-004"
    embedding_dim: int = 768

    # --- Observability ---
    langsmith_api_key: str | None = None
    langsmith_project: str = "finsight"
    langsmith_tracing: bool = False

    # --- File storage ---
    cloudinary_cloud_name: str | None = None
    cloudinary_api_key: str | None = None
    cloudinary_api_secret: str | None = None

    @property
    def is_prod(self) -> bool:
        return self.environment == "prod"


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor — used as a FastAPI dependency."""
    return Settings()
