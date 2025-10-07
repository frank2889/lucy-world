from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

from backend.extensions import db
from backend.models import Payment, User
from backend.services.metrics import collect_entitlement_metrics


def test_collect_entitlement_metrics_window(monkeypatch, app):
    fixed_now = datetime(2024, 10, 7, 12, 0, 0)

    monkeypatch.setattr("backend.services.metrics.utcnow", lambda: fixed_now)
    monkeypatch.setattr("backend.models.utcnow", lambda: fixed_now)

    with app.app_context():
        trial_user = User(
            email="trial@example.com",
            name="Trial User",
            api_token="token-trial",
            plan="trial",
            plan_started_at=fixed_now - timedelta(days=13),
            created_at=fixed_now - timedelta(days=13),
            plan_metadata={"tier": "free", "ai_credits": 0},
        )
        pro_user = User(
            email="pro@example.com",
            name="Pro User",
            api_token="token-pro",
            plan="pro",
            plan_started_at=fixed_now - timedelta(days=1),
            created_at=fixed_now - timedelta(days=1),
            plan_metadata={"tier": "pro", "ai_credits": 0},
        )
        expired_trial = User(
            email="expired@example.com",
            name="Expired Trial",
            api_token="token-expired",
            plan="trial",
            plan_started_at=fixed_now - timedelta(days=16),
            created_at=fixed_now - timedelta(days=16),
            plan_metadata={"tier": "free", "ai_credits": 0},
        )

        db.session.add_all([trial_user, pro_user, expired_trial])
        db.session.flush()

        successful_payment = Payment(
            user_id=pro_user.id,
            processor="stripe",
            order_id="order-paid",
            status="PAID",
            amount=Decimal("99.00"),
            net_amount=Decimal("90.00"),
            tax_amount=Decimal("9.00"),
            currency="EUR",
            created_at=fixed_now - timedelta(days=1),
        )

        failed_payment = Payment(
            user_id=trial_user.id,
            processor="stripe",
            order_id="order-failed",
            status="FAILED",
            amount=Decimal("49.00"),
            net_amount=Decimal("49.00"),
            tax_amount=Decimal("0.00"),
            currency="EUR",
            created_at=fixed_now - timedelta(days=2),
        )

        db.session.add_all([successful_payment, failed_payment])
        db.session.commit()

        metrics = collect_entitlement_metrics(window_days=14)

        users = metrics["users"]
        assert users["total"] == 3
        assert users["paying"] == 1
        assert users["new_signups"] == 2
        assert users["new_upgrades"] == 1
        assert users["trial_expiring_soon"] == 1
        assert users["trial_expired_recently"] == 1
        assert users["plans"]["pro"] == 1
        assert users["plans"]["trial"] == 1
        assert users["plans"]["trial_expired"] == 1

        payments = metrics["payments"]
        assert payments["total"] == 2
        assert payments["successful"] == 1
        assert payments["failed"] == 1
        assert payments["customers_with_success"] == 1
        assert payments["status_breakdown"]["PAID"] == 1
        assert payments["status_breakdown"]["FAILED"] == 1
        assert payments["gross_amount"] == 99.0
        assert payments["net_amount"] == 90.0
        assert payments["tax_amount"] == 9.0
        assert payments["gross_amount_all"] == 148.0
        assert payments["net_amount_all"] == 139.0
        assert payments["tax_amount_all"] == 9.0
        assert payments["average_order_value"] == 99.0