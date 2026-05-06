"""Deduplication layer for URLs and extracted content."""

from app.dedup.fingerprint import FingerprintDeduplicator

__all__ = ["FingerprintDeduplicator"]
