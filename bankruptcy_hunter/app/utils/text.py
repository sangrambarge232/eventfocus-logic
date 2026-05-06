"""Text normalization helpers for multilingual matching and deduplication."""

from __future__ import annotations

import re
import unicodedata

_WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(value: str) -> str:
    """Normalize unicode, trim whitespace, and lowercase text for matching."""

    normalized = unicodedata.normalize("NFKC", value or "")
    normalized = _WHITESPACE_RE.sub(" ", normalized).strip()
    return normalized.casefold()
