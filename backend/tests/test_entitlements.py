from __future__ import annotations

from datetime import datetime
from backend.extensions import db
from backend.models import User


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


def test_entitlements_custom_urls_and_expiry(client, app, monkeypatch):
    monkeypatch.setenv("ENTITLEMENTS_UPGRADE_URL", "https://billing.example.com/upgrade")
    monkeypatch.setenv("ENTITLEMENTS_BUY_CREDITS_URL", "https://billing.example.com/credits")

    with app.app_context():
        user = User.create("vip@example.com")
        user.plan = "enterprise"
        meta = dict(user.plan_metadata or {})
        meta.update({
            "tier": "enterprise",
            "ai_credits": 250,
            "expires_at": "2026-01-01T12:30:45Z",
        })
        user.plan_metadata = meta
        db.session.commit()
        token = user.api_token

    response = client.get(
        "/api/entitlements",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["tier"] == "enterprise"
    assert payload["ai_credits"] == 250
    assert payload["upgrade_url"] == "https://billing.example.com/upgrade"
    assert payload["buy_credits_url"] == "https://billing.example.com/credits"
    assert payload["expires_at"] == "2026-01-01T12:30:45Z"

