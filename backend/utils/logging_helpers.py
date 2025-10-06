from __future__ import annotations

import json
import logging
from typing import Any
from uuid import uuid4

from flask import g, has_request_context, request

_LOGGER_NAME = "lucy.observability"


def _ensure_correlation_id() -> str:
    if has_request_context():
        if getattr(g, "correlation_id", None):
            return g.correlation_id  # type: ignore[return-value]
        incoming = request.headers.get("X-Request-ID") or request.headers.get("X-Correlation-ID")
        cid = incoming or str(uuid4())
        g.correlation_id = cid  # type: ignore[assignment]
        return cid
    return str(uuid4())


def structured_log(event: str, *, level: int = logging.INFO, **fields: Any) -> None:
    """Emit a JSON-formatted log entry with a correlation identifier."""
    correlation_id = fields.pop("correlation_id", None) or _ensure_correlation_id()
    payload = {
        "event": event,
        "correlation_id": correlation_id,
        **fields,
    }
    logger = logging.getLogger(_LOGGER_NAME)
    logger.log(level, json.dumps(payload, sort_keys=True))


def correlation_id() -> str:
    """Return the active correlation identifier (generates one if missing)."""
    return _ensure_correlation_id()
