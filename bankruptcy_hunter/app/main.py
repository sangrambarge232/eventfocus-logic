"""FastAPI application entry point for BankruptcyHunter."""

from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import router
from app.config import get_settings
from app.db import initialize_database
from app.utils.logging import configure_logging

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Multilingual bankruptcy and financial distress web-searching platform.",
)
app.include_router(router, prefix="/api")


@app.on_event("startup")
def startup() -> None:
    """Initialize local resources before serving traffic."""

    initialize_database()
