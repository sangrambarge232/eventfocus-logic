"""Translation abstraction for multilingual workflows."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class TranslationLayer:
    """Translation facade with a safe pass-through default.

    TODO: Wire a production translation backend after credentials or local model
    decisions are available (for example Hugging Face NLLB, MarianMT, or a cloud
    translation API). The interface is intentionally stable for downstream code.
    """

    def translate(self, text: str, *, source_language: str | None = None, target_language: str = "en") -> str:
        """Translate text into ``target_language`` or return original text locally."""

        logger.debug("Translation requested source=%s target=%s", source_language, target_language)
        return text
