from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Union

Number = Union[int, float]


def utcnow() -> datetime:
    """Return a naive UTC datetime compatible with existing database columns."""
    return datetime.now(UTC).replace(tzinfo=None)


def utc_today() -> date:
    """Return the current UTC date."""
    return utcnow().date()


def to_utc_isoformat(dt: datetime | None = None) -> str:
    """Format a datetime as an ISO 8601 string in UTC with trailing Z."""
    base = dt or datetime.now(UTC)
    if base.tzinfo is None:
        base = base.replace(tzinfo=UTC)
    else:
        base = base.astimezone(UTC)
    base = base.replace(microsecond=0)
    return base.isoformat().replace("+00:00", "Z")


def from_timestamp_utc(value: Number) -> datetime:
    """Convert an epoch value (seconds) to a naive UTC datetime."""
    return datetime.fromtimestamp(float(value), UTC).replace(tzinfo=None)
