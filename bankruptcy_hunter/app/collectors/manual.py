"""Manual URL ingestion for analysts and dashboard submissions."""

from __future__ import annotations

from urllib.parse import urlparse

from app.collectors.base import CollectedItem
from app.utils.errors import IngestionError


class ManualUrlCollector:
    """Validate analyst-supplied URLs before downstream extraction."""

    def collect(self, urls: list[str], *, source: str = "manual") -> list[CollectedItem]:
        """Convert HTTP(S) URLs into collected items."""

        items: list[CollectedItem] = []
        for url in urls:
            parsed = urlparse(url.strip())
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                raise IngestionError(f"Invalid URL for manual ingestion: {url}")
            items.append(CollectedItem(url=parsed.geturl(), source=source))
        return items
