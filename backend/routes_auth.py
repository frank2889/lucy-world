from __future__ import annotations

import os
import secrets
from datetime import datetime, timedelta
from urllib.parse import urlencode

from flask import Blueprint, jsonify, request

from .extensions import db
from .models import User, LoginToken
from .email_utils import send_email


bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@bp.route('/request', methods=['POST'])
def request_magic_link():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    name = (data.get('name') or '').strip() or None
    if not email:
        return jsonify({'error': 'email required'}), 400
    # Create or get user without password
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User.create(email=email, name=name)
    # Create login token
    token = secrets.token_urlsafe(24)
    expires = datetime.utcnow() + timedelta(minutes=20)
    lt = LoginToken(email=email, token=token, expires_at=expires)
    db.session.add(lt)
    db.session.commit()

    base = os.getenv('PUBLIC_BASE_URL') or request.url_root.rstrip('/')
    verify_url = f"{base}/api/auth/verify?{urlencode({'token': token})}"
    # Email content
    subject = "Your Lucy World sign-in link"
    body = (
        f"Hello{(' ' + (name or '')).strip()},\n\n"
        f"Click the secure link below to sign in. This link expires in 20 minutes and can be used only once.\n\n"
        f"{verify_url}\n\n"
        f"If you did not request this, you can ignore this email.\n"
    )
    send_email(email, subject, body)
    return jsonify({'ok': True})


@bp.route('/verify', methods=['GET', 'POST'])
def verify_magic_link():
    token = request.args.get('token') or ((request.get_json() or {}).get('token') if request.is_json else None)
    if not token:
        return jsonify({'error': 'token required'}), 400
    lt = LoginToken.query.filter_by(token=token).first()
    if not lt or lt.used:
        return jsonify({'error': 'invalid token'}), 400
    if lt.expires_at < datetime.utcnow():
        return jsonify({'error': 'token expired'}), 400
    # Get or create user
    user = User.query.filter_by(email=lt.email).first()
    if not user:
        user = User.create(email=lt.email)
    # Mark token used
    lt.used = True
    db.session.commit()

    # If the client expects JSON (e.g., API call), return JSON
    accept = (request.headers.get('Accept') or '').lower()
    if 'application/json' in accept or request.method == 'POST':
        return jsonify({'id': user.id, 'email': user.email, 'name': user.name, 'token': user.api_token})
    else:
        # Otherwise return a small HTML page that stores token then redirects to /<lang>/
        # The page reads lw_lang from localStorage to pick the UI language.
        page = """
<!doctype html>
<html lang="en"><head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Signing you in…</title>
</head><body style="font-family: system-ui, -apple-system, Segoe UI, Roboto; padding: 24px;">
  <h3>Signing you in…</h3>
  <p>You can close this tab if it doesn't redirect automatically.</p>
  <script>
    try {
      localStorage.setItem('lw_token', '__TOKEN__');
      var lang = (localStorage.getItem('lw_lang') || 'en').toLowerCase();
      if (!/^[a-z]{2}$/.test(lang)) lang = 'en';
      location.replace('/' + lang + '/');
    } catch (e) {
      location.replace('/');
    }
  </script>
</body></html>
        """
        page = page.replace('__TOKEN__', user.api_token)
        return page, 200, {'Content-Type': 'text/html; charset=utf-8'}
