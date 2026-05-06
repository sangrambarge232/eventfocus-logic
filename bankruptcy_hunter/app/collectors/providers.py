"""Search provider registry and local starter adapter implementations."""

from __future__ import annotations

from dataclasses import dataclass, field
import logging

from app.collectors.base import CollectedItem, SearchProvider

logger = logging.getLogger(__name__)


@dataclass
class SearchProviderRegistry:
    """In-memory registry for search provider adapters.

    TODO: Add adapters for production providers after API keys are available
    (for example Bing Web Search, Google Programmable Search, SerpAPI, or GDELT).
    """

    providers: dict[str, SearchProvider] = field(default_factory=dict)

    def register(self, provider: SearchProvider) -> None:
        """Register a provider by its unique name."""

        logger.info("Registering search provider: %s", provider.name)
        self.providers[provider.name] = provider

    def search_all(self, query: str, *, language: str | None = None, limit: int = 10) -> list[CollectedItem]:
        """Execute a query across every registered provider and merge results."""

        results: list[CollectedItem] = []
        for provider in self.providers.values():
            try:
                results.extend(provider.search(query, language=language, limit=limit))
            except Exception as exc:  # noqa: BLE001 - provider isolation is intentional.
                logger.exception("Provider %s failed for query %r: %s", provider.name, query, exc)
        return results


class DisabledProvider:
    """Documented no-op provider used until external search credentials exist."""

    name = "disabled-provider"

    def search(self, query: str, *, language: str | None = None, limit: int = 10) -> list[CollectedItem]:
        """Return no results while documenting the adapter contract."""

        logger.warning("No external search provider configured for query=%r language=%r", query, language)
        return []
