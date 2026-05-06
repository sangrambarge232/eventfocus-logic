"""Multilingual bankruptcy and financial distress keyword matching."""

from __future__ import annotations

from dataclasses import dataclass

from app.utils.text import normalize_text


DEFAULT_KEYWORDS: dict[str, list[str]] = {
    "en": ["bankruptcy", "insolvency", "chapter 11", "liquidation", "debt restructuring"],
    "es": ["bancarrota", "insolvencia", "quiebra", "reestructuración de deuda"],
    "fr": ["faillite", "insolvabilité", "redressement judiciaire", "liquidation"],
    "de": ["insolvenz", "konkurs", "restrukturierung", "zahlungsunfähigkeit"],
    "pt": ["falência", "insolvência", "recuperação judicial", "reestruturação de dívida"],
}


@dataclass(slots=True)
class KeywordHit:
    """A matched keyword and the language bucket where it was configured."""

    keyword: str
    language: str


class KeywordMatcher:
    """Find multilingual distress keywords in article text."""

    def __init__(self, keywords: dict[str, list[str]] | None = None) -> None:
        self.keywords = keywords or DEFAULT_KEYWORDS

    def match(self, text: str) -> list[KeywordHit]:
        """Return all unique keyword hits found in normalized text."""

        normalized = normalize_text(text)
        hits: list[KeywordHit] = []
        for language, terms in self.keywords.items():
            for term in terms:
                if normalize_text(term) in normalized:
                    hits.append(KeywordHit(keyword=term, language=language))
        return hits
