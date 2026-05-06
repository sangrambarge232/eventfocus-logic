"""RSS and Atom ingestion support."""

from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.request import Request, urlopen
import logging
import xml.etree.ElementTree as ET

from app.collectors.base import CollectedItem
from app.config import get_settings
from app.utils.errors import IngestionError

logger = logging.getLogger(__name__)


class RssCollector:
    """Collect candidates from RSS or Atom feeds using standard-library XML parsing."""

    def fetch(self, feed_url: str, *, limit: int = 25) -> list[CollectedItem]:
        """Download and parse an RSS/Atom feed into collected items."""

        settings = get_settings()
        try:
            request = Request(feed_url, headers={"User-Agent": settings.user_agent})
            with urlopen(request, timeout=settings.request_timeout_seconds) as response:
                payload = response.read()
        except Exception as exc:  # noqa: BLE001 - wraps network/parser details.
            raise IngestionError(f"Unable to fetch feed {feed_url}: {exc}") from exc

        try:
            root = ET.fromstring(payload)
        except ET.ParseError as exc:
            raise IngestionError(f"Feed {feed_url} is not valid XML: {exc}") from exc

        items = self._parse_rss(root, feed_url) or self._parse_atom(root, feed_url)
        logger.info("Parsed %s items from feed %s", len(items[:limit]), feed_url)
        return items[:limit]

    def _parse_rss(self, root: ET.Element, feed_url: str) -> list[CollectedItem]:
        items: list[CollectedItem] = []
        for item in root.findall(".//item"):
            url = (item.findtext("link") or "").strip()
            if not url:
                continue
            items.append(
                CollectedItem(
                    url=url,
                    title=(item.findtext("title") or "").strip(),
                    source=feed_url,
                    published_at=_parse_date(item.findtext("pubDate")),
                )
            )
        return items

    def _parse_atom(self, root: ET.Element, feed_url: str) -> list[CollectedItem]:
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        items: list[CollectedItem] = []
        for entry in root.findall(".//atom:entry", ns):
            link = entry.find("atom:link", ns)
            url = link.attrib.get("href", "").strip() if link is not None else ""
            if not url:
                continue
            items.append(
                CollectedItem(
                    url=url,
                    title=(entry.findtext("atom:title", default="", namespaces=ns) or "").strip(),
                    source=feed_url,
                    published_at=_parse_date(entry.findtext("atom:updated", default="", namespaces=ns)),
                )
            )
        return items


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
