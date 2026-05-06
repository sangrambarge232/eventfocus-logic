"""Collectors for search providers, RSS feeds, and manual URL ingestion."""

from app.collectors.base import CollectedItem, SearchProvider
from app.collectors.manual import ManualUrlCollector
from app.collectors.rss import RssCollector

__all__ = ["CollectedItem", "SearchProvider", "ManualUrlCollector", "RssCollector"]
