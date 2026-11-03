"""Application settings, read from environment variables (or backend/.env locally)."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="BRAVE_", extra="ignore")

    environment: Literal["local", "test", "staging", "production"] = "local"

    # Plain PostgreSQL connection string. Works the same for local Docker,
    # Supabase in months 1-2 (test data only) and AWS RDS from month 3.
    # The API connects as a low-privilege role that cannot bypass Row-Level Security.
    database_url: str = "postgresql+psycopg://brave_app:brave_app@localhost:5432/brave"

    # Migrations connect as the schema owner (brave_owner). Falls back to database_url.
    migration_database_url: str | None = None

    # Origins allowed to call the API from a browser (the React app).
    cors_origins: list[str] = ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
