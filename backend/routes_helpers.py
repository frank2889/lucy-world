from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Optional, TypeVar

from flask import jsonify, request, g

from .models import User

F = TypeVar("F", bound=Callable[..., Any])


def _resolve_token() -> str:
    auth = request.headers.get("Authorization", "")
    token = ""
    if auth.startswith("Bearer "):
        token = auth.split(" ", 1)[1].strip()
    if not token:
        token = (request.args.get("token") or request.headers.get("X-API-Token") or "").strip()
    return token


def auth_required(fn: F) -> F:
    @wraps(fn)
    def wrapper(*args: Any, **kwargs: Any):
        token = _resolve_token()
        if not token:
            return jsonify({"error": "Unauthorized"}), 401
        user: Optional[User] = User.query.filter_by(api_token=token).first()
        if not user:
            return jsonify({"error": "Invalid token"}), 401
        # Store on both request and g for backward compatibility
        request.user = user  # type: ignore[attr-defined]
        g.current_user = user  # type: ignore[attr-defined]
        return fn(*args, **kwargs)

    return wrapper  # type: ignore[return-value]


def get_current_user() -> User:
    user = getattr(g, "current_user", None)
    if user is None:
        raise RuntimeError("auth_required decorator must run before accessing current user")
    return user
