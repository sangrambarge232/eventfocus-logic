"""Classification layer for bankruptcy relevance decisions."""

from __future__ import annotations

from dataclasses import dataclass

from app.ml.keywords import KeywordHit, KeywordMatcher


@dataclass(slots=True)
class ClassificationResult:
    """Classifier output consumed by scoring and API responses."""

    label: str
    confidence: float
    keyword_hits: list[KeywordHit]


class RuleBasedClassifier:
    """Starter classifier that uses keyword density until ML models are wired."""

    def __init__(self, matcher: KeywordMatcher | None = None) -> None:
        self.matcher = matcher or KeywordMatcher()

    def classify(self, text: str) -> ClassificationResult:
        """Classify text as bankruptcy-related or not."""

        hits = self.matcher.match(text)
        confidence = min(0.95, 0.25 + (0.15 * len(hits))) if hits else 0.05
        label = "financial_distress" if hits else "not_relevant"
        return ClassificationResult(label=label, confidence=round(confidence, 3), keyword_hits=hits)
