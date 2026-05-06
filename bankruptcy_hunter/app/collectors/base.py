"""Base interfaces for BankruptcyHunter collection adapters."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Protocol


@dataclass(slots=True)
class CollectedItem:
    """Raw candidate returned by an RSS feed, search provider, or manual input."""

    url: str
    title: str = ""
    source: str = "unknown"
    language_hint: str | None = None
    published_at: datetime | None = None
    metadata: dict[str, str] = field(default_factory=dict)
    collected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class SearchProvider(Protocol):
    """Adapter protocol for pluggable web search providers."""

    name: str

    def search(self, query: str, *, language: str | None = None, limit: int = 10) -> list[CollectedItem]:
        """Return normalized search results for a query."""
