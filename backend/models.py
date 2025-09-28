from __future__ import annotations

import secrets
from datetime import datetime
from typing import Optional

from .extensions import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    api_token = db.Column(db.String(64), unique=True, nullable=False, index=True)

    projects = db.relationship('Project', backref='owner', lazy=True, cascade='all, delete-orphan')

    @staticmethod
    def create(email: str, name: Optional[str] = None) -> 'User':
        token = secrets.token_hex(24)
        user = User(email=email.strip().lower(), name=name, api_token=token)
        db.session.add(user)
        db.session.commit()
        return user


class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    language = db.Column(db.String(8), nullable=True)
    country = db.Column(db.String(2), nullable=True)
    data = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @staticmethod
    def create(user: User, name: str, description: Optional[str] = None, language: Optional[str] = None, country: Optional[str] = None, data: Optional[dict] = None) -> 'Project':
        proj = Project(user_id=user.id, name=name, description=description, language=language, country=country, data=data or {})
        db.session.add(proj)
        db.session.commit()
        return proj


class LoginToken(db.Model):
    __tablename__ = 'login_tokens'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), index=True, nullable=False)
    token = db.Column(db.String(128), unique=True, index=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)

