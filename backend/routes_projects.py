from __future__ import annotations

from functools import wraps
from typing import Callable, Optional

from flask import Blueprint, jsonify, request

from .extensions import db
from .models import User, Project


bp = Blueprint('projects', __name__, url_prefix='/api')


def auth_required(fn: Callable):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        token = ''
        if auth.startswith('Bearer '):
            token = auth.split(' ', 1)[1].strip()
        if not token:
            token = request.args.get('token', '')
        if not token:
            return jsonify({'error': 'Unauthorized'}), 401
        user: Optional[User] = User.query.filter_by(api_token=token).first()
        if not user:
            return jsonify({'error': 'Invalid token'}), 401
        request.user = user  # type: ignore[attr-defined]
        return fn(*args, **kwargs)
    return wrapper


@bp.route('/me', methods=['GET'])
@auth_required
def me():
    u: User = request.user  # type: ignore
    return jsonify({'id': u.id, 'email': u.email, 'name': u.name, 'token': u.api_token})


@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    name = (data.get('name') or '').strip() or None
    if not email:
        return jsonify({'error': 'email required'}), 400
    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({'id': existing.id, 'email': existing.email, 'name': existing.name, 'token': existing.api_token})
    user = User.create(email=email, name=name)
    return jsonify({'id': user.id, 'email': user.email, 'name': user.name, 'token': user.api_token}), 201


@bp.route('/projects', methods=['GET'])
@auth_required
def list_projects():
    u: User = request.user  # type: ignore
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
    p = Project.query.filter_by(id=pid, user_id=u.id).first()
    if not p:
        return jsonify({'error': 'not found'}), 404
    db.session.delete(p)
    db.session.commit()
    return jsonify({'ok': True})
