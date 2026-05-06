"""Hugging Face model registry support."""

from __future__ import annotations

from dataclasses import dataclass, asdict
import json
from pathlib import Path

from app.config import get_settings
from app.utils.errors import ModelRegistryError


@dataclass(slots=True)
class ModelSpec:
    """Metadata for a Hugging Face model used by BankruptcyHunter."""

    task: str
    model_id: str
    revision: str = "main"
    description: str = ""


class ModelRegistry:
    """Read and write simple JSON model registry files."""

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path or get_settings().huggingface_model_registry)

    def load(self) -> list[ModelSpec]:
        """Load registered Hugging Face models from disk."""

        if not self.path.exists():
            return []
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            return [ModelSpec(**item) for item in payload.get("models", [])]
        except (OSError, TypeError, ValueError) as exc:
            raise ModelRegistryError(f"Invalid model registry at {self.path}: {exc}") from exc

    def save(self, models: list[ModelSpec]) -> None:
        """Persist model metadata as formatted JSON."""

        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps({"models": [asdict(model) for model in models]}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
