"""Risk and priority scoring for extracted articles."""

from __future__ import annotations

from dataclasses import dataclass

from app.ml.classifier import ClassificationResult


@dataclass(slots=True)
class ScoreResult:
    """Normalized article score with analyst-friendly priority."""

    score: float
    priority: str
    reasons: list[str]


class ScoringEngine:
    """Convert classification evidence into a 0-100 priority score."""

    def score(self, classification: ClassificationResult) -> ScoreResult:
        """Score an article using confidence and number of keyword hits."""

        base = classification.confidence * 70
        keyword_bonus = min(30, len(classification.keyword_hits) * 6)
        score = round(min(100, base + keyword_bonus), 2)
        priority = "high" if score >= 75 else "medium" if score >= 40 else "low"
        reasons = [f"classification={classification.label}", f"keyword_hits={len(classification.keyword_hits)}"]
        return ScoreResult(score=score, priority=priority, reasons=reasons)
