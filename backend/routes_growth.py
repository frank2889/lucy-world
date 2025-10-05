from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from flask import Blueprint, current_app, jsonify, request

from backend.extensions import db
from backend.models import CandidateQuery, ContentDraft
from backend.services.ai_blog_pipeline import DraftGenerationError

bp = Blueprint("growth", __name__, url_prefix="/api/growth")


def _pipeline():
    pipeline = current_app.extensions.get("growth_pipeline")
    if not pipeline:
        raise RuntimeError("growth pipeline not configured")
    return pipeline


def _serialize_candidate(candidate: CandidateQuery) -> Dict[str, Any]:
    latest_draft = None
    if candidate.drafts:
        latest_draft = max(candidate.drafts, key=lambda d: d.created_at or datetime.min)
    return {
        "id": candidate.id,
        "keyword": candidate.keyword,
        "language": candidate.language,
        "country": candidate.country,
        "audience_score": candidate.audience_score,
        "threshold_reason": candidate.threshold_reason,
        "status": candidate.status,
        "created_at": candidate.created_at.isoformat() if candidate.created_at else None,
        "updated_at": candidate.updated_at.isoformat() if candidate.updated_at else None,
        "latest_draft_id": latest_draft.id if latest_draft else None,
        "latest_draft_status": latest_draft.status if latest_draft else None,
    }


def _serialize_draft(draft: ContentDraft) -> Dict[str, Any]:
    return {
        "id": draft.id,
        "candidate_id": draft.candidate_id,
        "slug": draft.slug,
        "title": draft.title,
        "summary": draft.summary,
        "status": draft.status,
        "language": draft.language,
        "country": draft.country,
        "author": draft.author_name,
        "tags": draft.tags or [],
        "created_at": draft.created_at.isoformat() if draft.created_at else None,
        "updated_at": draft.updated_at.isoformat() if draft.updated_at else None,
        "published_at": draft.published_at.isoformat() if draft.published_at else None,
    }


@bp.route("/candidates", methods=["GET"])
def list_candidates():
    limit = min(max(int(request.args.get("limit", 50) or 50), 1), 200)
    status = request.args.get("status")
    query = CandidateQuery.query
    if status:
        query = query.filter(CandidateQuery.status == status)
    query = query.order_by(CandidateQuery.audience_score.desc(), CandidateQuery.created_at.desc())
    candidates = query.limit(limit).all()
    return jsonify([_serialize_candidate(candidate) for candidate in candidates])


@bp.route("/drafts", methods=["GET"])
def list_drafts():
    limit = min(max(int(request.args.get("limit", 50) or 50), 1), 200)
    status = request.args.get("status")
    query = ContentDraft.query
    if status:
        query = query.filter(ContentDraft.status == status)
    query = query.order_by(ContentDraft.created_at.desc())
    drafts = query.limit(limit).all()
    return jsonify([_serialize_draft(draft) for draft in drafts])


@bp.route("/drafts/<int:draft_id>", methods=["GET"])
def get_draft(draft_id: int):
    draft = ContentDraft.query.get_or_404(draft_id)
    return jsonify(_serialize_draft(draft))


@bp.route("/drafts/run", methods=["POST"])
def run_pipeline():
    try:
        pipeline = _pipeline()
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503

    payload = request.get_json(silent=True) or {}
    limit = payload.get("limit", 1)
    try:
        limit_value = min(max(int(limit), 1), 10)
    except (TypeError, ValueError):
        limit_value = 1

    pending = (
        CandidateQuery.query.filter(CandidateQuery.status == "pending")
        .order_by(CandidateQuery.audience_score.desc(), CandidateQuery.created_at.asc())
        .limit(limit_value)
        .all()
    )

    generated: List[Dict[str, Any]] = []
    failures: List[Dict[str, Any]] = []

    for candidate in pending:
        try:
            draft = pipeline.generate_from_candidate(candidate)
        except DraftGenerationError as exc:
            candidate.status = "failed"
            db.session.commit()
            failures.append({"candidate_id": candidate.id, "error": str(exc)})
            continue
        generated.append({
            "candidate_id": candidate.id,
            "draft_id": draft.id,
            "slug": draft.slug,
            "status": draft.status,
        })

    return jsonify({
        "processed": len(pending),
        "generated": generated,
        "failed": failures,
    })


@bp.route("/drafts/<int:draft_id>/publish", methods=["POST"])
def publish_draft(draft_id: int):
    try:
        pipeline = _pipeline()
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503

    draft = ContentDraft.query.get_or_404(draft_id)
    payload = request.get_json(silent=True) or {}
    tags = payload.get("tags") if isinstance(payload.get("tags"), list) else None

    try:
        pipeline.publish_draft(
            draft,
            author=payload.get("author"),
            tags=tags,
            language=payload.get("language"),
            country=payload.get("country"),
        )
    except DraftGenerationError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(_serialize_draft(draft))


@bp.route("/manifest", methods=["GET"])
def manifest():
    try:
        pipeline = _pipeline()
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
    return jsonify(pipeline.latest_manifest())
