"""SQLite-first database connection helpers with PostgreSQL-ready settings."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import sqlite3
from typing import Iterator

from app.config import get_settings

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL DEFAULT '',
    language TEXT,
    label TEXT NOT NULL DEFAULT 'pending',
    confidence REAL NOT NULL DEFAULT 0,
    score REAL NOT NULL DEFAULT 0,
    priority TEXT NOT NULL DEFAULT 'low',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Yield a SQLite connection for local development.

    Production deployments can replace this module with SQLAlchemy engine/session
    factories while keeping ``DATABASE_URL`` configured for PostgreSQL.
    """

    settings = get_settings()
    if not settings.database_url.startswith("sqlite:///"):
        raise RuntimeError("Only SQLite connections are enabled in the starter; configure SQLAlchemy for production.")
    db_path = Path(settings.database_url.replace("sqlite:///", "", 1))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def initialize_database() -> None:
    """Create local development tables if they do not already exist."""

    with get_connection() as connection:
        connection.executescript(SCHEMA_SQL)
