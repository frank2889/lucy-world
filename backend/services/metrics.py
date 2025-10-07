from __future__ import annotations

from collections import Counter
from datetime import timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import func

from ..extensions import db
from ..models import (
	TRIAL_DURATION_DAYS,
	Payment,
	User,
	calculate_trial_expiry,
	effective_plan_slug,
)
from ..utils import structured_log, to_utc_isoformat, utcnow

_WINDOW_DEFAULT_DAYS = 7
_TRIAL_EXPIRY_LOOKAHEAD_DAYS = 3
_SUCCESS_STATUSES = {"PAID", "SUCCEEDED", "SUCCESS", "COMPLETED"}


def _decimal_to_float(value: Decimal | float | None) -> float:
	if value is None:
		return 0.0
	if isinstance(value, Decimal):
		return float(value)
	return float(value)


def _to_decimal(value: Decimal | float | int | str | None) -> Decimal:
	if value is None:
		return Decimal("0")
	if isinstance(value, Decimal):
		return value
	return Decimal(str(value))


def collect_entitlement_metrics(*, window_days: int = _WINDOW_DEFAULT_DAYS) -> dict[str, Any]:
	"""Collect aggregate entitlement and billing metrics for observability dashboards."""

	window_days = max(1, int(window_days))
	now = utcnow()
	window_start = now - timedelta(days=window_days)

	session = db.session

	user_rows = session.query(User.plan, User.plan_started_at, User.created_at).all()
	plan_counter: Counter[str] = Counter()
	trial_expiring_soon = 0
	trial_expired_recently = 0

	horizon = now + timedelta(days=_TRIAL_EXPIRY_LOOKAHEAD_DAYS)
	for plan, plan_started_at, created_at in user_rows:
		slug = effective_plan_slug(plan, plan_started_at)
		plan_counter[slug] += 1

		expiry = calculate_trial_expiry(plan_started_at, created_at)
		if not expiry:
			continue
		if slug == "trial" and now <= expiry <= horizon:
			trial_expiring_soon += 1
		if slug == "trial_expired" and window_start <= expiry <= now:
			trial_expired_recently += 1

	total_users = sum(plan_counter.values())
	paying_users = plan_counter.get("pro", 0) + plan_counter.get("enterprise", 0)

	new_signups = session.query(func.count(User.id)).filter(User.created_at >= window_start).scalar() or 0
	new_upgrades = (
		session.query(func.count(User.id))
		.filter(User.plan.in_(["pro", "enterprise"]))
		.filter(User.plan_started_at >= window_start)
		.scalar()
		or 0
	)

	payment_rows = (
		session.query(
			Payment.status,
			Payment.amount,
			Payment.net_amount,
			Payment.tax_amount,
			Payment.user_id,
		)
		.filter(Payment.created_at >= window_start)
		.all()
	)

	status_counter: Counter[str] = Counter()
	gross_total_all = Decimal("0")
	net_total_all = Decimal("0")
	tax_total_all = Decimal("0")
	gross_total_success = Decimal("0")
	net_total_success = Decimal("0")
	tax_total_success = Decimal("0")
	success_customers: set[int] = set()

	for status, amount, net_amount, tax_amount, user_id in payment_rows:
		normalized_status = (status or "UNKNOWN").upper()
		status_counter[normalized_status] += 1

		if amount is not None:
			amount_decimal = _to_decimal(amount)
			gross_total_all += amount_decimal
		else:
			amount_decimal = None
		if net_amount is not None:
			net_decimal = _to_decimal(net_amount)
			net_total_all += net_decimal
		else:
			net_decimal = None
		if tax_amount is not None:
			tax_decimal = _to_decimal(tax_amount)
			tax_total_all += tax_decimal
		else:
			tax_decimal = None

		if normalized_status in _SUCCESS_STATUSES:
			if user_id is not None:
				success_customers.add(user_id)
			if amount_decimal is not None:
				gross_total_success += amount_decimal
			if net_decimal is not None:
				net_total_success += net_decimal
			if tax_decimal is not None:
				tax_total_success += tax_decimal

	successful_payments = sum(status_counter[s] for s in _SUCCESS_STATUSES if s in status_counter)
	failed_payments = sum(
		count for status, count in status_counter.items() if status not in _SUCCESS_STATUSES
	)

	avg_order_value = (
		float(gross_total_success / successful_payments)
		if successful_payments
		else 0.0
	)

	metrics: dict[str, Any] = {
		"generated_at": to_utc_isoformat(now),
		"window": {
			"days": window_days,
			"start": to_utc_isoformat(window_start),
			"end": to_utc_isoformat(now),
		},
		"users": {
			"total": total_users,
			"paying": paying_users,
			"plans": dict(plan_counter),
			"new_signups": int(new_signups),
			"new_upgrades": int(new_upgrades),
			"trial_expiring_soon": trial_expiring_soon,
			"trial_expired_recently": trial_expired_recently,
			"trial_expiry_lookahead_days": _TRIAL_EXPIRY_LOOKAHEAD_DAYS,
			"trial_duration_days": TRIAL_DURATION_DAYS,
		},
		"payments": {
			"total": len(payment_rows),
			"successful": successful_payments,
			"failed": failed_payments,
			"status_breakdown": dict(status_counter),
			"customers_with_success": len(success_customers),
			"gross_amount": _decimal_to_float(gross_total_success),
			"net_amount": _decimal_to_float(net_total_success),
			"tax_amount": _decimal_to_float(tax_total_success),
			"gross_amount_all": _decimal_to_float(gross_total_all),
			"net_amount_all": _decimal_to_float(net_total_all),
			"tax_amount_all": _decimal_to_float(tax_total_all),
			"average_order_value": avg_order_value,
		},
	}

	structured_log(
		"metrics.collected",
		window_days=window_days,
		total_users=total_users,
		paying_users=paying_users,
		payments_successful=successful_payments,
		gross_amount=metrics["payments"]["gross_amount"],
	)

	return metrics