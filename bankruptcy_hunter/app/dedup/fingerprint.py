"""Content fingerprint based deduplication."""

from __future__ import annotations

import hashlib

from app.utils.text import normalize_text


class FingerprintDeduplicator:
    """Track URL and text fingerprints in memory for a single run."""

    def __init__(self) -> None:
        self._seen: set[str] = set()

    def fingerprint(self, *, url: str, text: str = "") -> str:
        """Build a stable SHA-256 fingerprint from URL and normalized text."""

        material = f"{normalize_text(url)}\n{normalize_text(text)[:5000]}"
        return hashlib.sha256(material.encode("utf-8")).hexdigest()

    def is_duplicate(self, *, url: str, text: str = "") -> bool:
        """Return True if the item has already been observed in this run."""

        digest = self.fingerprint(url=url, text=text)
        if digest in self._seen:
            return True
        self._seen.add(digest)
        return False
