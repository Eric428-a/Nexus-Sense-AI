"""
Timestamp utilities.
"""

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Return the current timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


def timestamp_iso() -> str:
    """Return the current UTC timestamp in ISO-8601 format."""
    return utc_now().isoformat()