"""Core smoke tests for BankruptcyHunter starter components."""

from app.collectors.manual import ManualUrlCollector
from app.ml.classifier import RuleBasedClassifier
from app.scoring import ScoringEngine


def test_rule_based_classifier_scores_bankruptcy_text() -> None:
    """Bankruptcy-related text should receive a relevant label and nonzero score."""

    result = RuleBasedClassifier().classify("The company filed for Chapter 11 bankruptcy protection.")
    score = ScoringEngine().score(result)
    assert result.label == "financial_distress"
    assert score.score > 0


def test_manual_url_collector_accepts_https_url() -> None:
    """Manual ingestion should normalize valid HTTPS URLs."""

    items = ManualUrlCollector().collect(["https://example.com/story"])
    assert items[0].url == "https://example.com/story"
