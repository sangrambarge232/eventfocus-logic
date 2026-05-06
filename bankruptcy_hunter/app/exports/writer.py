"""Export BankruptcyHunter results to analyst-friendly files."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from openpyxl import Workbook

from app.config import get_settings


class ExportWriter:
    """Write normalized result dictionaries to CSV or Excel workbooks."""

    def __init__(self, export_dir: str | Path | None = None) -> None:
        self.export_dir = Path(export_dir or get_settings().export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def to_csv(self, rows: list[dict[str, Any]], filename: str = "bankruptcy_hunter_results.csv") -> Path:
        """Write rows to CSV and return the created path."""

        path = self.export_dir / filename
        fieldnames = sorted({key for row in rows for key in row.keys()}) if rows else ["message"]
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows or [{"message": "No results"}])
        return path

    def to_excel(self, rows: list[dict[str, Any]], filename: str = "bankruptcy_hunter_results.xlsx") -> Path:
        """Write rows to an XLSX workbook and return the created path."""

        path = self.export_dir / filename
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Results"
        fieldnames = sorted({key for row in rows for key in row.keys()}) if rows else ["message"]
        sheet.append(fieldnames)
        for row in rows or [{"message": "No results"}]:
            sheet.append([row.get(field) for field in fieldnames])
        workbook.save(path)
        return path
