"""Compatibility package exposing repository-level BankruptcyHunter loaders."""

from src.file_loader import (
    FileLoaderError,
    load_bankruptcy_examples,
    load_bankruptcy_rulebook,
    load_complaints_tracker_sample,
    load_eventwatch_industries,
    load_notification_tracker_sample,
)

__all__ = [
    "FileLoaderError",
    "load_bankruptcy_examples",
    "load_bankruptcy_rulebook",
    "load_complaints_tracker_sample",
    "load_eventwatch_industries",
    "load_notification_tracker_sample",
]
