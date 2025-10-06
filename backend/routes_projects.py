from __future__ import annotations

from flask import Blueprint, jsonify, request

from .extensions import db
from .models import DailyUsage, Project, User
from .routes_helpers import auth_required
from .utils import utc_today


def _plan_snapshot(user: User) -> dict:
    today = utc_today()
    usage = DailyUsage.for_day(user, today)
    queries_used = usage.query_count if usage else 0
    return user.plan_payload(include_usage=True, queries_used_today=queries_used)


bp = Blueprint('projects', __name__, url_prefix='/api')


@bp.route('/me', methods=['GET'])
@auth_required
def me():
    u: User = request.user  # type: ignore
    usage_snapshot = _plan_snapshot(u)
    return jsonify({
        'id': u.id,
        'email': u.email,
        'name': u.name,
        'token': u.api_token,
        'plan': usage_snapshot,
    })


@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    name = (data.get('name') or '').strip() or None
    if not email:
        return jsonify({'error': 'email required'}), 400
    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({
            'id': existing.id,
            'email': existing.email,
            'name': existing.name,
            'token': existing.api_token,
            'plan': _plan_snapshot(existing),
        })
    user = User.create(email=email, name=name)
    return jsonify({
        'id': user.id,
        'email': user.email,
        'name': user.name,
        'token': user.api_token,
        'plan': _plan_snapshot(user),
    }), 201


@bp.route('/projects', methods=['GET'])
@auth_required
def list_projects():
    u: User = request.user  # type: ignore
    if not u.has_feature('projects'):
        return jsonify({'error': 'plan_upgrade_required', 'plan': u.plan_payload()}), 403
    projs = Project.query.filter_by(user_id=u.id).order_by(Project.updated_at.desc()).all()
    return jsonify([
        {
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'language': p.language,
            'country': p.country,
            'updated_at': p.updated_at.isoformat()
        } for p in projs
    ])


@bp.route('/projects', methods=['POST'])
@auth_required
def create_project():
    u: User = request.user  # type: ignore
    if not u.has_feature('projects'):
        return jsonify({'error': 'plan_upgrade_required', 'plan': u.plan_payload()}), 403
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'name required'}), 400
    description = (data.get('description') or '').strip() or None
    language = (data.get('language') or '').strip().lower() or None
    country = (data.get('country') or '').strip().upper() or None
    payload = data.get('data') if isinstance(data.get('data'), dict) else None
    p = Project.create(u, name=name, description=description, language=language, country=country, data=payload)
    return jsonify({'id': p.id}), 201


@bp.route('/projects/<int:pid>', methods=['GET'])
@auth_required
def get_project(pid: int):
    u: User = request.user  # type: ignore
    if not u.has_feature('projects'):
        return jsonify({'error': 'plan_upgrade_required', 'plan': u.plan_payload()}), 403
    p = Project.query.filter_by(id=pid, user_id=u.id).first()
    if not p:
        return jsonify({'error': 'not found'}), 404
    return jsonify({
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'language': p.language,
        'country': p.country,
        'data': p.data,
        'created_at': p.created_at.isoformat(),
        'updated_at': p.updated_at.isoformat(),
    })


@bp.route('/projects/<int:pid>', methods=['PATCH'])
@auth_required
def update_project(pid: int):
    u: User = request.user  # type: ignore
    if not u.has_feature('projects'):
        return jsonify({'error': 'plan_upgrade_required', 'plan': u.plan_payload()}), 403
    p = Project.query.filter_by(id=pid, user_id=u.id).first()
    if not p:
        return jsonify({'error': 'not found'}), 404
    data = request.get_json() or {}
    if 'name' in data:
        name = (data.get('name') or '').strip()
        if not name:
            return jsonify({'error': 'name cannot be empty'}), 400
        p.name = name
    if 'description' in data:
        p.description = (data.get('description') or '').strip() or None
    if 'language' in data:
        p.language = (data.get('language') or '').strip().lower() or None
    if 'country' in data:
        p.country = (data.get('country') or '').strip().upper() or None
    if 'data' in data and isinstance(data.get('data'), dict):
        p.data = data.get('data')
    db.session.commit()
    return jsonify({'ok': True})


@bp.route('/projects/<int:pid>', methods=['DELETE'])
@auth_required
def delete_project(pid: int):
    u: User = request.user  # type: ignore
    if not u.has_feature('projects'):
        return jsonify({'error': 'plan_upgrade_required', 'plan': u.plan_payload()}), 403
    p = Project.query.filter_by(id=pid, user_id=u.id).first()
    if not p:
        return jsonify({'error': 'not found'}), 404
    db.session.delete(p)
    db.session.commit()
    return jsonify({'ok': True})
