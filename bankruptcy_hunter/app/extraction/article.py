"""Article downloading and lightweight text extraction."""

from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.request import Request, urlopen
import logging

from app.config import get_settings
from app.utils.errors import ExtractionError

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class Article:
    """Extracted article content ready for NLP processing."""

    url: str
    title: str
    text: str
    language: str | None = None
    raw_html: str | None = None


class ArticleExtractor:
    """Fetch pages and extract readable starter text without external services."""

    def extract(self, url: str) -> Article:
        """Fetch a URL and produce a normalized article object."""

        settings = get_settings()
        try:
            request = Request(url, headers={"User-Agent": settings.user_agent})
            with urlopen(request, timeout=settings.request_timeout_seconds) as response:
                raw_html = response.read().decode(response.headers.get_content_charset() or "utf-8", errors="replace")
        except Exception as exc:  # noqa: BLE001 - wraps network/encoding details.
            raise ExtractionError(f"Unable to extract article from {url}: {exc}") from exc

        parser = _ReadableTextParser()
        parser.feed(raw_html)
        text = " ".join(part.strip() for part in parser.text_parts if part.strip())
        if not text:
            raise ExtractionError(f"No readable text found at {url}")
        logger.info("Extracted %s characters from %s", len(text), url)
        return Article(url=url, title=parser.title.strip(), text=text, raw_html=raw_html)


class _ReadableTextParser(HTMLParser):
    """Minimal HTML parser that captures title, paragraph, heading, and list text."""

    readable_tags = {"p", "h1", "h2", "h3", "li", "article"}

    def __init__(self) -> None:
        super().__init__()
        self._tag_stack: list[str] = []
        self.title = ""
        self.text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._tag_stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()

    def handle_data(self, data: str) -> None:
        if not self._tag_stack:
            return
        current = self._tag_stack[-1]
        if current == "title":
            self.title += data
        elif current in self.readable_tags:
            self.text_parts.append(data)
