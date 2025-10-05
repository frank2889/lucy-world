from __future__ import annotations

from flask import Blueprint, jsonify, request, Response

from .models import User
from .services.entitlements import build_entitlements

bp = Blueprint("entitlements", __name__, url_prefix="/api")


def _resolve_user() -> User | None:
    token = (request.headers.get("Authorization") or "").strip()
    candidate = ""
    if token.lower().startswith("bearer "):
        candidate = token.split(" ", 1)[1].strip()
    if not candidate:
        candidate = (request.args.get("token") or request.headers.get("X-API-Token") or "").strip()
    if not candidate:
        return None
    return User.query.filter_by(api_token=candidate).first()


@bp.route("/entitlements", methods=["GET"])
def entitlements() -> Response:
    user = _resolve_user()
    entitlements = build_entitlements(user, request)
    return jsonify(entitlements.to_dict())
