from __future__ import annotations

from src.seen_articles import canonicalise_url, mark_seen


def mark_seen_url(url: str) -> tuple[bool, str]:
    """Mark a URL as seen and return (inserted, canonical_url)."""
    canonical_url = canonicalise_url(url)
    inserted = mark_seen(canonical_url)
    return inserted, canonical_url