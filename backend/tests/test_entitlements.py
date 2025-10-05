from __future__ import annotations

from typing import Generator

import pytest  # type: ignore

from backend import create_app
from backend.extensions import db
from backend.models import User


@pytest.fixture
def app(monkeypatch, tmp_path) -> Generator:
    db_file = tmp_path / "test.sqlite3"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file}")
    monkeypatch.setenv("PUBLIC_BASE_URL", "https://example.com")
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_entitlements_anonymous_defaults(client):
    response = client.get("/api/entitlements")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["tier"] == "free"
    assert payload["ai_credits"] == 0
    assert payload["sidebar_groups"] == ["search"]
    assert payload["upgrade_url"].startswith("https://example.com")


def test_entitlements_pro_with_ai(client, app):
    with app.app_context():
        user = User.create("pro@example.com")
        user.plan = "pro"
        meta = dict(user.plan_metadata or {})
        meta["tier"] = "pro"
        meta["ai_credits"] = 120
        user.plan_metadata = meta
        db.session.commit()
        token = user.api_token
    refreshed = User.query.filter_by(api_token=token).first()
    assert refreshed is not None
    assert refreshed.plan == "pro"
    assert (refreshed.plan_metadata or {}).get("tier") == "pro"

    response = client.get(
        "/api/entitlements",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["tier"] == "pro"
    assert "ai" in payload["sidebar_groups"]
    assert payload["ai_credits"] == 120


def test_entitlements_handles_invalid_token(client):
    response = client.get(
        "/api/entitlements",
        headers={"Authorization": "Bearer invalid"},
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["tier"] == "free"
    assert payload["ai_credits"] == 0

