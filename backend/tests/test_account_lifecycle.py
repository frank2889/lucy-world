from __future__ import annotations

import pytest

from backend.models import LoginToken, User
from backend.routes_billing import (
    _handle_checkout_completed,
    _handle_invoice_paid,
    _handle_subscription_cancelled,
)
from backend.services.credits import consume_ai_credit
from backend.extensions import db


def _sign_webhook(payload: dict, secret: str, timestamp: int) -> tuple[str, str]:
    import hashlib
    import hmac
    import json

    body = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    message = f"{timestamp}.{body}".encode()
    signature = hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()
    return body, f"t={timestamp},v1={signature}"


@pytest.fixture(autouse=True)
def _patch_email(monkeypatch) -> None:
    def _fake_send(to_email: str, subject: str, body: str) -> None:
        pass

    monkeypatch.setattr("backend.routes_auth.send_email", _fake_send)


def _create_user(email: str) -> User:
    return User.create(email=email)


def test_magic_link_signup_yields_free_entitlements(client, app):
    response = client.post("/api/auth/request", json={"email": "new@lucy.world"})
    assert response.status_code == 200

    with app.app_context():
        user = User.query.filter_by(email="new@lucy.world").one()
        token = LoginToken.query.filter_by(email="new@lucy.world").one()
        assert user.plan_metadata["tier"] == "free"
        assert user.plan_metadata["ai_credits"] == 0
        assert user.stripe_customer_id is None

    verify = client.get(
        f"/api/auth/verify?token={token.token}",
        headers={"Accept": "application/json"},
    )
    assert verify.status_code == 200
    payload = verify.get_json()
    assert payload["plan"]["metadata"]["tier"] == "free"

    entitlements = client.get(
        "/api/entitlements",
        headers={"Authorization": f"Bearer {payload['token']}"},
    )
    data = entitlements.get_json()
    assert data["tier"] == "free"
    assert data["sidebar_groups"] == ["search"]


def test_checkout_session_completed_promotes_user(app):
    with app.app_context():
        user = _create_user("pro@lucy.world")
        session = {
            "id": "cs_test_123",
            "metadata": {"user_id": str(user.id)},
            "customer": "cus_test_123",
            "subscription": "sub_test_123",
            "customer_details": {
                "name": "Pro User",
                "email": "pro@lucy.world",
                "address": {"country": "NL"},
            },
            "expires_at": 1_700_000_000,
        }
        assert _handle_checkout_completed(session)
        assert user.plan == "pro"
        assert user.plan_metadata["tier"] == "pro"
        assert user.plan_metadata["stripe"]["subscription_id"] == "sub_test_123"


def test_invoice_paid_grants_ai_credits(monkeypatch, app):
    monkeypatch.setenv("STRIPE_PRICE_PRO_USAGE", "price_ai_pack_100")
    monkeypatch.setenv("STRIPE_AI_CREDITS_PER_UNIT", "100")
    sample_invoice = {
        "id": "in_test_123",
        "customer": "cus_test_123",
        "amount_paid": 1399,
        "tax": 0,
        "currency": "eur",
        "status": "paid",
        "lines": {
            "data": [
                {
                    "id": "il_base",
                    "price": {"id": "price_base"},
                    "quantity": 1,
                    "period": {"end": 1_700_001_000},
                },
                {
                    "id": "il_usage",
                    "price": {"id": "price_ai_pack_100"},
                    "quantity": 2,
                },
            ]
        },
    }

    with app.app_context():
        user = _create_user("usage@lucy.world")
        user.stripe_customer_id = "cus_test_123"
        assert _handle_invoice_paid(sample_invoice)
        assert user.plan_metadata["tier"] == "pro"
        assert user.plan_metadata["ai_credits"] == 200
        events = user.plan_metadata.get("credit_events") or []
        assert events and events[-1]["type"] == "grant"

        balance = consume_ai_credit(user, amount=60, reason="generate.ai")
        assert balance == 140
        assert user.plan_metadata["ai_credits"] == 140


def test_webhook_invoice_paid_integration(monkeypatch, client, app):
    secret = "dummy_webhook_secret"
    monkeypatch.setenv("STRIPE_SECRET_KEY", "dummy_secret_key")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", secret)
    monkeypatch.setenv("STRIPE_PRICE_PRO_USAGE", "price_ai_pack_50")
    monkeypatch.setenv("STRIPE_AI_CREDITS_PER_UNIT", "50")
    monkeypatch.setattr(
        "stripe.Webhook.construct_event",
        lambda payload, sig_header, webhook_secret: __import__("json").loads(payload),
    )

    with app.app_context():
        user = _create_user("webhook@lucy.world")
        user.stripe_customer_id = "cus_webhook_123"
        db.session.commit()

    invoice_object = {
        "id": "in_webhook_123",
        "customer": "cus_webhook_123",
        "amount_paid": 1099,
        "tax": 0,
        "currency": "eur",
        "status": "paid",
        "lines": {
            "data": [
                {
                    "id": "il_usage",
                    "price": {"id": "price_ai_pack_50"},
                    "quantity": 3,
                    "period": {"end": 1_700_100_000},
                }
            ]
        },
    }
    payload = {"type": "invoice.paid", "data": {"object": invoice_object}}
    timestamp = 1_700_000_000
    body, signature = _sign_webhook(payload, secret, timestamp)

    response = client.post(
        "/api/billing/webhook",
        data=body,
        headers={"Stripe-Signature": signature, "Content-Type": "application/json"},
    )
    assert response.status_code == 200
    assert response.get_json()["handled"] is True

    with app.app_context():
        user = User.query.filter_by(email="webhook@lucy.world").one()
        assert user.plan == "pro"
        assert user.plan_metadata["ai_credits"] == 150
        events = user.plan_metadata.get("credit_events") or []
        assert events and events[-1]["type"] == "grant"


def test_subscription_cancelled_downgrades_user(app):
    with app.app_context():
        user = _create_user("downgrade@lucy.world")
        user.plan = "pro"
        user.stripe_subscription_id = "sub_test_456"
        meta = dict(user.plan_metadata or {})
        meta["tier"] = "pro"
        user.plan_metadata = meta

        payload = {"id": "sub_test_456", "status": "canceled"}
        assert _handle_subscription_cancelled(payload)
        assert user.plan == "trial_expired"
        assert user.plan_metadata["tier"] == "free"


def test_anonymous_entitlements_match_free_marketing_copy(client):
    response = client.get("/api/entitlements")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["tier"] == "free"
    assert payload["sidebar_groups"] == ["search"]
    assert payload["upgrade_url"].endswith("/billing/upgrade")