"""Smoke tests for EventWatch input file loading."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from src.file_loader import (
    BANKRUPTCY_EXAMPLES_FILE,
    COMPLAINTS_TRACKER_FILE,
    FileLoaderError,
    INDUSTRIES_FILE,
    NOTIFICATION_TRACKER_FILE,
    RULEBOOK_FILE,
    load_bankruptcy_examples,
    load_bankruptcy_rulebook,
    load_complaints_tracker_sample,
    load_eventwatch_industries,
    load_notification_tracker_sample,
)


def test_required_file_missing_message_names_required_file(tmp_path: Path) -> None:
    """Required inputs should fail with a message that names the missing file."""

    with pytest.raises(FileLoaderError) as exc_info:
        load_bankruptcy_rulebook(tmp_path)
    assert RULEBOOK_FILE in str(exc_info.value)


def test_optional_trackers_missing_return_empty_samples(tmp_path: Path) -> None:
    """Optional tracker workbooks should never crash local startup when absent."""

    assert load_notification_tracker_sample(tmp_path) == []
    assert load_complaints_tracker_sample(tmp_path) == []


def test_load_eventwatch_industries_deduplicates_allowed_universe(tmp_path: Path) -> None:
    """Industry loading should preserve order while removing duplicates."""

    _write_csv(tmp_path / INDUSTRIES_FILE, ["Industry"], [["Retail"], ["Energy"], ["retail"]])

    assert load_eventwatch_industries(tmp_path) == ["Retail", "Energy"]


def test_load_bankruptcy_rulebook_extracts_only_relevant_guidance(tmp_path: Path) -> None:
    """Rulebook loading should keep bankruptcy guidance and required important terms."""

    (tmp_path / RULEBOOK_FILE).write_text(
        "EVENTWATCH_RULEBOOK = {"
        "'Bankruptcy and Financial Distress': {'must_report': ['bankruptcy proceedings']},"
        "'Leadership': {'ignore': ['CEO appointment']}"
        "}",
        encoding="utf-8",
    )

    loaded = load_bankruptcy_rulebook(tmp_path)

    assert "bankruptcy" in loaded["important_terms"]
    assert "missed payment" in loaded["important_terms"]
    assert "Bankruptcy and Financial Distress" in loaded["guidance"]
    assert "Leadership" not in loaded["guidance"]


def test_load_bankruptcy_examples_splits_report_and_exclusion_rows(tmp_path: Path) -> None:
    """Training examples should split MUST Report from DO NOT Report rows."""

    _write_csv(
        tmp_path / BANKRUPTCY_EXAMPLES_FILE,
        ["Company", "Decision", "Event Description"],
        [
            ["Acme", "MUST Report", "Acme entered bankruptcy proceedings."],
            ["Beta", "DO NOT Report", "Beta hired a new CFO."],
        ],
    )

    loaded = load_bankruptcy_examples(tmp_path)

    assert loaded["positive_examples"][0]["Company"] == "Acme"
    assert loaded["exclusion_examples"][0]["Company"] == "Beta"


def test_optional_tracker_constants_document_input_filenames() -> None:
    """Constants should preserve exact user-provided workbook names."""

    assert NOTIFICATION_TRACKER_FILE.startswith("EventWatch Notifications Tracker")
    assert COMPLAINTS_TRACKER_FILE.startswith("2025 - EventWatch Complaints")


def _write_csv(path: Path, headers: list[str], rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)
