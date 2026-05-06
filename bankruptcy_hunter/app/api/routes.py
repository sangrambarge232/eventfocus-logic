"""HTTP API routes for ingestion, classification, health, and exports."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.collectors.manual import ManualUrlCollector
from app.ml.classifier import RuleBasedClassifier
from app.scoring import ScoringEngine
from app.utils.errors import BankruptcyHunterError

router = APIRouter()


class AnalyzeTextRequest(BaseModel):
    """Request body for direct text analysis."""

    text: str = Field(min_length=1, description="Article or snippet text to classify.")


class ManualUrlRequest(BaseModel):
    """Request body for manual URL ingestion."""

    urls: list[str] = Field(min_length=1, description="HTTP(S) URLs to enqueue for extraction.")


@router.get("/health")
def health() -> dict[str, str]:
    """Return process health for load balancers and smoke tests."""

    return {"status": "ok", "service": "BankruptcyHunter"}


@router.post("/analyze-text")
def analyze_text(request: AnalyzeTextRequest) -> dict[str, object]:
    """Classify and score caller-provided text."""

    classification = RuleBasedClassifier().classify(request.text)
    score = ScoringEngine().score(classification)
    return {
        "label": classification.label,
        "confidence": classification.confidence,
        "keyword_hits": [hit.__dict__ for hit in classification.keyword_hits],
        "score": score.score,
        "priority": score.priority,
        "reasons": score.reasons,
    }


@router.post("/ingest/manual")
def ingest_manual(request: ManualUrlRequest) -> dict[str, object]:
    """Validate manual URLs and return normalized queued items."""

    try:
        items = ManualUrlCollector().collect(request.urls)
    except BankruptcyHunterError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"count": len(items), "items": [item.__dict__ for item in items]}
