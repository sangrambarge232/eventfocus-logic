"""Centralized logging configuration for BankruptcyHunter."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configure_logging(level: str = "INFO", log_file: str = "logs/bankruptcy_hunter.log") -> None:
    """Configure console and rotating file logging.

    The function is idempotent enough for tests and local scripts: if handlers
    already exist on the root logger, their level is updated without duplicating
    output streams.
    """

    root = logging.getLogger()
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    root.setLevel(numeric_level)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    if not root.handlers:
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        root.addHandler(console)

        path = Path(log_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(path, maxBytes=2_000_000, backupCount=5)
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

    for handler in root.handlers:
        handler.setLevel(numeric_level)
