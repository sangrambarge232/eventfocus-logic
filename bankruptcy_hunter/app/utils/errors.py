"""Domain-specific exceptions used across BankruptcyHunter."""


class BankruptcyHunterError(Exception):
    """Base exception for recoverable application errors."""


class IngestionError(BankruptcyHunterError):
    """Raised when a feed, URL, or provider cannot be ingested."""


class ExtractionError(BankruptcyHunterError):
    """Raised when an article cannot be extracted into useful text."""


class ModelRegistryError(BankruptcyHunterError):
    """Raised when model registry metadata is invalid or unavailable."""
