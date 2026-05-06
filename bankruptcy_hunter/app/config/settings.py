"""Runtime settings for local and production BankruptcyHunter deployments."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import os


@dataclass(frozen=True)
class Settings:
    """Typed environment-backed application settings.

    SQLite is the default for local development. Set ``DATABASE_URL`` to a
    PostgreSQL DSN in production, for example
    ``postgresql+psycopg://user:password@host:5432/bankruptcy_hunter``.
    """

    app_name: str = "BankruptcyHunter"
    environment: str = os.getenv("APP_ENV", "local")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///data/bankruptcy_hunter.db")
    default_language: str = os.getenv("DEFAULT_LANGUAGE", "en")
    huggingface_model_registry: str = os.getenv("HF_MODEL_REGISTRY", "data/model_registry.json")
    export_dir: Path = Path(os.getenv("EXPORT_DIR", "data/exports"))
    request_timeout_seconds: float = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "20"))
    user_agent: str = os.getenv("USER_AGENT", "BankruptcyHunter/0.1 (+local-dev)")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings loaded from environment variables."""

    settings = Settings()
    settings.export_dir.mkdir(parents=True, exist_ok=True)
    return settings
