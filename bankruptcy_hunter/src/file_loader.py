"""Load EventWatch source files for the BankruptcyHunter prototype.

The loader centralizes all access to analyst-provided files in ``data/input`` so
API routes and dashboards can consume sanitized bankruptcy-specific structures
without exposing internal training, tracker, or complaints files to users.
Required files raise clear :class:`FileLoaderError` messages when unavailable;
optional tracker files log a warning and return an empty sample.
"""

from __future__ import annotations

import ast
import csv
import importlib
import importlib.util
import logging
from pathlib import Path
from typing import Any, Iterable

logger = logging.getLogger(__name__)

INPUT_DIR = Path("data/input")
RULEBOOK_FILE = "eventwatch_rulebook(4).py"
INDUSTRIES_FILE = "eventwatch_industries(1).csv"
BANKRUPTCY_EXAMPLES_FILE = "bankruptcy_events_100_full.csv"
NOTIFICATION_TRACKER_FILE = "EventWatch Notifications Tracker (2021 - onwards) - Copy (3)(1).xlsx"
COMPLAINTS_TRACKER_FILE = "2025 - EventWatch Complaints (3)(1).xlsx"

REQUIRED_FILES = (RULEBOOK_FILE, INDUSTRIES_FILE, BANKRUPTCY_EXAMPLES_FILE)
OPTIONAL_FILES = (NOTIFICATION_TRACKER_FILE, COMPLAINTS_TRACKER_FILE)

IMPORTANT_BANKRUPTCY_TERMS = (
    "bankruptcy",
    "insolvency",
    "possible bankruptcy",
    "signs of bankruptcy",
    "talks of bankruptcy",
    "missed payment",
    "default payment",
    "parent bankruptcy",
    "subsidiary bankruptcy",
    "bankruptcy proceedings",
)

_BANKRUPTCY_GUIDANCE_KEYS = (
    "bankruptcy",
    "financial distress",
    "financial_distress",
    "insolvency",
    "distress",
)

_POSITIVE_LABELS = {"must report", "must_report", "must-report", "report", "yes", "positive"}
_EXCLUSION_LABELS = {
    "do not report",
    "do_not_report",
    "do-not-report",
    "dont report",
    "don't report",
    "no",
    "negative",
    "exclude",
}


class FileLoaderError(RuntimeError):
    """Raised when a required EventWatch input file is missing or invalid."""


def load_eventwatch_industries(input_dir: str | Path = INPUT_DIR) -> list[str]:
    """Load the allowed EventWatch industry universe from ``eventwatch_industries(1).csv``.

    The returned list is de-duplicated while preserving file order. Dashboard and
    classification code should use this as the only allowed industry universe.
    """

    path = _required_path(input_dir, INDUSTRIES_FILE)
    rows = _read_csv_rows(path)
    industries: list[str] = []
    seen: set[str] = set()

    for row in rows:
        industry = _first_present_value(
            row,
            preferred_columns=("industry", "industries", "eventwatch industry", "sector"),
        )
        if not industry:
            industry = next((value for value in row.values() if value.strip()), "")
        normalized = " ".join(industry.split())
        if normalized and normalized.casefold() not in seen:
            industries.append(normalized)
            seen.add(normalized.casefold())

    if not industries:
        raise FileLoaderError(
            f"Required industry file '{path}' did not contain any usable industries. "
            "Expected a CSV column such as 'Industry' or non-empty first-column values."
        )
    return industries


def load_bankruptcy_rulebook(input_dir: str | Path = INPUT_DIR) -> dict[str, Any]:
    """Load Bankruptcy and Financial Distress guidance from ``EVENTWATCH_RULEBOOK``.

    Only rulebook branches whose key path references bankruptcy, insolvency, or
    financial distress are retained for this prototype. The returned dictionary
    always includes ``important_terms`` containing the required bankruptcy terms.
    """

    path = _required_path(input_dir, RULEBOOK_FILE)
    rulebook = _load_eventwatch_rulebook_dict(path)
    guidance = _extract_guidance(rulebook)
    return {
        "source_file": path.name,
        "important_terms": list(IMPORTANT_BANKRUPTCY_TERMS),
        "guidance": guidance,
    }


def load_bankruptcy_examples(input_dir: str | Path = INPUT_DIR) -> dict[str, list[dict[str, str]]]:
    """Load bankruptcy training/evaluation examples from CSV.

    Rows marked ``MUST Report`` become positive examples. Rows marked
    ``DO NOT Report`` become exclusion examples. This function is intended for
    internal filtering tests and must not be used to populate dashboard tables.
    """

    path = _required_path(input_dir, BANKRUPTCY_EXAMPLES_FILE)
    rows = _read_csv_rows(path)
    positive_examples: list[dict[str, str]] = []
    exclusion_examples: list[dict[str, str]] = []

    for row in rows:
        label = _detect_report_label(row)
        if label in _POSITIVE_LABELS:
            positive_examples.append(row)
        elif label in _EXCLUSION_LABELS:
            exclusion_examples.append(row)

    if not positive_examples and not exclusion_examples:
        raise FileLoaderError(
            f"Required examples file '{path}' did not contain rows marked 'MUST Report' "
            "or 'DO NOT Report'. Check the report/label column names and values."
        )

    return {
        "positive_examples": positive_examples,
        "exclusion_examples": exclusion_examples,
    }


def load_notification_tracker_sample(
    input_dir: str | Path = INPUT_DIR,
    *,
    limit: int = 25,
) -> list[dict[str, Any]]:
    """Load a small internal sample from the historical EventWatch tracker workbook.

    Missing optional tracker files do not crash the application; an empty list is
    returned after logging a clear warning. The sample is for internal modeling
    context and should not be displayed on the dashboard.
    """

    path = _optional_path(input_dir, NOTIFICATION_TRACKER_FILE)
    if path is None:
        return []
    return _read_xlsx_sample(path, limit=limit)


def load_complaints_tracker_sample(
    input_dir: str | Path = INPUT_DIR,
    *,
    limit: int = 25,
) -> list[dict[str, Any]]:
    """Load a small internal sample from the customer complaints tracker workbook.

    Complaints examples provide evidence that missed and delayed events must be
    avoided. Missing optional files do not crash the application and return an
    empty list after logging a warning.
    """

    path = _optional_path(input_dir, COMPLAINTS_TRACKER_FILE)
    if path is None:
        return []
    return _read_xlsx_sample(path, limit=limit)


def _required_path(input_dir: str | Path, filename: str) -> Path:
    """Resolve and validate a required input file path."""

    path = _resolve_input_dir(input_dir) / filename
    if not path.exists():
        required = ", ".join(REQUIRED_FILES)
        raise FileLoaderError(
            f"Missing required EventWatch input file: '{path}'. Place '{filename}' in "
            f"'{path.parent}'. Required files are: {required}."
        )
    if not path.is_file():
        raise FileLoaderError(f"Required EventWatch input path exists but is not a file: '{path}'.")
    return path


def _optional_path(input_dir: str | Path, filename: str) -> Path | None:
    """Resolve an optional input file path, logging a warning if it is absent."""

    path = _resolve_input_dir(input_dir) / filename
    if not path.exists():
        logger.warning(
            "Optional EventWatch tracker file is missing: %s. Continuing without this internal sample.",
            path,
        )
        return None
    if not path.is_file():
        logger.warning(
            "Optional EventWatch tracker path exists but is not a file: %s. Continuing without this sample.",
            path,
        )
        return None
    return path


def _resolve_input_dir(input_dir: str | Path) -> Path:
    """Resolve ``data/input`` from common working directories."""

    candidate = Path(input_dir)
    if candidate.is_absolute() or candidate.exists():
        return candidate

    package_root_candidate = Path(__file__).resolve().parents[1] / candidate
    if package_root_candidate.exists():
        return package_root_candidate

    repository_candidate = Path(__file__).resolve().parents[2] / candidate
    if repository_candidate.exists():
        return repository_candidate

    return candidate


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read a UTF-8/UTF-8-SIG CSV into normalized string dictionaries."""

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                raise FileLoaderError(f"CSV file '{path}' has no header row.")
            return [
                {str(key or "").strip(): str(value or "").strip() for key, value in row.items()}
                for row in reader
            ]
    except UnicodeDecodeError as exc:
        raise FileLoaderError(f"CSV file '{path}' must be UTF-8 or UTF-8-SIG encoded: {exc}") from exc
    except OSError as exc:
        raise FileLoaderError(f"Unable to read CSV file '{path}': {exc}") from exc


def _load_eventwatch_rulebook_dict(path: Path) -> dict[str, Any]:
    """Parse the literal ``EVENTWATCH_RULEBOOK`` assignment from a Python file."""

    try:
        module_ast = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        raise FileLoaderError(f"Rulebook file '{path}' is not valid Python: {exc}") from exc
    except OSError as exc:
        raise FileLoaderError(f"Unable to read rulebook file '{path}': {exc}") from exc

    for node in module_ast.body:
        value_node: ast.AST | None = None
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == "EVENTWATCH_RULEBOOK" for target in node.targets):
                value_node = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id == "EVENTWATCH_RULEBOOK":
                value_node = node.value

        if value_node is not None:
            try:
                value = ast.literal_eval(value_node)
            except (ValueError, TypeError) as exc:
                raise FileLoaderError(
                    f"EVENTWATCH_RULEBOOK in '{path}' must be a literal dictionary so it can be loaded safely."
                ) from exc
            if not isinstance(value, dict):
                raise FileLoaderError(f"EVENTWATCH_RULEBOOK in '{path}' must be a dictionary.")
            return value

    raise FileLoaderError(f"Rulebook file '{path}' does not define EVENTWATCH_RULEBOOK.")


def _extract_guidance(rulebook: dict[str, Any]) -> dict[str, Any]:
    """Return only bankruptcy/financial-distress branches from a nested rulebook."""

    extracted = _walk_guidance(rulebook, key_path=())
    return extracted if isinstance(extracted, dict) else {}


def _walk_guidance(value: Any, *, key_path: tuple[str, ...]) -> Any | None:
    """Recursively retain values whose keys or descendants match target guidance terms."""

    path_matches = _key_path_matches(key_path)
    if isinstance(value, dict):
        retained: dict[str, Any] = {}
        for key, child in value.items():
            key_text = str(key)
            child_value = _walk_guidance(child, key_path=(*key_path, key_text))
            if child_value is not None:
                retained[key_text] = child_value
        if retained:
            return retained
        return value if path_matches else None

    if isinstance(value, list):
        retained_items = [
            item
            for item in (_walk_guidance(item, key_path=key_path) for item in value)
            if item is not None
        ]
        if retained_items:
            return retained_items
        return value if path_matches or _text_matches(value) else None

    return value if path_matches or _text_matches(value) else None


def _key_path_matches(key_path: Iterable[str]) -> bool:
    """Return whether any key in a nested path references the prototype scope."""

    joined = " ".join(key_path).casefold().replace("_", " ").replace("-", " ")
    return any(term.replace("_", " ") in joined for term in _BANKRUPTCY_GUIDANCE_KEYS)


def _text_matches(value: Any) -> bool:
    """Return whether scalar or list values reference bankruptcy/distress terms."""

    if isinstance(value, list):
        text = " ".join(str(item) for item in value)
    else:
        text = str(value)
    normalized = text.casefold().replace("_", " ").replace("-", " ")
    return any(term.replace("_", " ") in normalized for term in _BANKRUPTCY_GUIDANCE_KEYS)


def _first_present_value(row: dict[str, str], *, preferred_columns: Iterable[str]) -> str:
    """Return the first value whose column name matches one of the preferred names."""

    normalized_row = {_normalize_column_name(key): value for key, value in row.items()}
    for column in preferred_columns:
        value = normalized_row.get(_normalize_column_name(column), "")
        if value.strip():
            return value.strip()
    return ""


def _detect_report_label(row: dict[str, str]) -> str:
    """Detect a MUST Report / DO NOT Report label from common column names or values."""

    preferred = _first_present_value(
        row,
        preferred_columns=(
            "reporting decision",
            "report decision",
            "decision",
            "label",
            "classification",
            "must report",
            "report?",
            "report",
        ),
    )
    candidates = [preferred, *row.values()]
    for value in candidates:
        normalized = _normalize_label(value)
        if normalized in _POSITIVE_LABELS or normalized in _EXCLUSION_LABELS:
            return normalized
    return ""


def _normalize_label(value: str) -> str:
    """Normalize reporting labels for robust comparison."""

    return " ".join(str(value or "").strip().casefold().replace("_", " ").replace("-", " ").split())


def _normalize_column_name(value: str) -> str:
    """Normalize column names for case/spacing-insensitive lookups."""

    return " ".join(str(value or "").strip().casefold().replace("_", " ").replace("-", " ").split())


def _read_xlsx_sample(path: Path, *, limit: int) -> list[dict[str, Any]]:
    """Read the first worksheet in an XLSX file into a bounded list of dictionaries."""

    if limit < 1:
        return []
    if importlib.util.find_spec("openpyxl") is None:
        raise FileLoaderError(
            f"Workbook '{path}' requires the optional dependency 'openpyxl'. "
            "Install project requirements before loading tracker samples."
        )
    load_workbook = importlib.import_module("openpyxl").load_workbook

    try:
        workbook = load_workbook(path, read_only=True, data_only=True)
    except OSError as exc:
        raise FileLoaderError(f"Unable to read workbook '{path}': {exc}") from exc
    except Exception as exc:  # noqa: BLE001 - openpyxl raises several parser exceptions.
        raise FileLoaderError(f"Workbook '{path}' could not be parsed as XLSX: {exc}") from exc

    try:
        sheet = workbook.active
        rows = sheet.iter_rows(values_only=True)
        headers = next(rows, None)
        if not headers:
            return []
        fieldnames = [str(header).strip() if header is not None else f"column_{index + 1}" for index, header in enumerate(headers)]
        sample: list[dict[str, Any]] = []
        for row in rows:
            record = {fieldnames[index]: value for index, value in enumerate(row) if index < len(fieldnames)}
            if any(value not in (None, "") for value in record.values()):
                sample.append(record)
            if len(sample) >= limit:
                break
        return sample
    finally:
        workbook.close()
