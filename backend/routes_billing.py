from __future__ import annotations

import json
import os
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

import stripe
from flask import Blueprint, current_app, jsonify, request

from .extensions import db
from .models import Payment, User
from .routes_helpers import auth_required, get_current_user

bp = Blueprint("billing", __name__, url_prefix="/api/billing")


class StripeConfigurationError(RuntimeError):
    """Raised when Stripe is not configured correctly."""


def _ensure_stripe_api() -> None:
    secret_key = (os.getenv("STRIPE_SECRET_KEY") or "").strip()
    if not secret_key:
        raise StripeConfigurationError(
            "Stripe secret key missing. Set STRIPE_SECRET_KEY in the environment."
        )
    if stripe.api_key != secret_key:
        stripe.api_key = secret_key


def _public_base_url() -> str:
    base = (os.getenv("PUBLIC_BASE_URL") or request.url_root or "").strip()
    if base.endswith("/"):
        base = base[:-1]
    return base or "http://localhost:5000"


def _price_ids() -> Dict[str, str]:
    base_price = (os.getenv("STRIPE_PRICE_PRO") or "").strip()
    usage_price = (os.getenv("STRIPE_PRICE_PRO_USAGE") or "").strip()
    if not base_price:
        raise StripeConfigurationError(
            "Stripe base price missing. Set STRIPE_PRICE_PRO with the recurring price ID."
        )
    payload = {"base": base_price}
    if usage_price:
        payload["usage"] = usage_price
    return payload


def _find_user_by_stripe(
    *,
    user_id: Optional[str] = None,
    customer_id: Optional[str] = None,
    email: Optional[str] = None,
) -> Optional[User]:
    user: Optional[User] = None
    if user_id:
        try:
            user = User.query.get(int(user_id))
        except (ValueError, TypeError):
            user = None
        if user:
            return user
    if customer_id:
        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        if user:
            return user
    if email:
        user = User.query.filter_by(email=email.lower()).first()
        if user:
            return user
    return None


@bp.route("/config", methods=["GET"])
@auth_required
def stripe_config() -> Any:
    publishable = (os.getenv("STRIPE_PUBLISHABLE_KEY") or "").strip()
    if not publishable:
        raise StripeConfigurationError(
            "Stripe publishable key missing. Set STRIPE_PUBLISHABLE_KEY in the environment."
        )
    return jsonify({"publishableKey": publishable})


@bp.route("/checkout-session", methods=["POST"])
@auth_required
def create_checkout_session() -> Any:
    user = get_current_user()
    try:
        _ensure_stripe_api()
        price_ids = _price_ids()
    except StripeConfigurationError as exc:
        return jsonify({"error": str(exc)}), 500

    customer_id = user.stripe_customer_id
    try:
        if not customer_id:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.name or user.email,
                metadata={"user_id": str(user.id)},
            )
            customer_id = customer.id
            user.stripe_customer_id = customer_id
            db.session.commit()
        else:
            # Ensure the Stripe customer still exists
            stripe.Customer.modify(customer_id, metadata={"user_id": str(user.id)})
    except Exception as exc:  # pragma: no cover - Stripe errors are runtime
        current_app.logger.error("Failed to initialize Stripe customer: %s", exc)
        return jsonify({"error": "Unable to create customer with Stripe."}), 502

    base_url = _public_base_url()
    line_items = [
        {
            "price": price_ids["base"],
            "quantity": 1,
        }
    ]
    if price_ids.get("usage"):
        line_items.append(
            {
                "price": price_ids["usage"],
                "quantity": 1,
            }
        )

    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            customer=customer_id,
            line_items=line_items,
            success_url=f"{base_url}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{base_url}/billing/cancel",
            billing_address_collection="required",
            automatic_tax={"enabled": True},
            metadata={"user_id": str(user.id)},
            subscription_data={
                "metadata": {"user_id": str(user.id)},
            },
            customer_update={"address": "auto", "name": "auto"},
        )
    except Exception as exc:  # pragma: no cover - Stripe errors are runtime
        current_app.logger.error("Failed to create checkout session: %s", exc)
        return jsonify({"error": "Unable to create Stripe checkout session."}), 502

    return jsonify({"url": session.url})


@bp.route("/customer-portal", methods=["POST"])
@auth_required
def create_customer_portal_session() -> Any:
    user = get_current_user()
    if not user.stripe_customer_id:
        return jsonify({"error": "no_stripe_customer"}), 400
    try:
        _ensure_stripe_api()
        session = stripe.billing_portal.Session.create(
            customer=user.stripe_customer_id,
            return_url=f"{_public_base_url()}/billing/portal",
        )
    except Exception as exc:  # pragma: no cover
        current_app.logger.error("Failed to create billing portal session: %s", exc)
        return jsonify({"error": "Unable to create billing portal session."}), 502
    return jsonify({"url": session.url})


@bp.route("/webhook", methods=["POST"])
def stripe_webhook() -> Any:
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature", "")
    webhook_secret = (os.getenv("STRIPE_WEBHOOK_SECRET") or "").strip()
    if not webhook_secret:
        current_app.logger.error("Stripe webhook secret is not configured.")
        return "Webhook secret not configured", 500

    try:
        _ensure_stripe_api()
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError:
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError:
        return "Invalid signature", 400
    except StripeConfigurationError:
        return "Stripe not configured", 500

    event_type = event.get("type")
    data = event.get("data", {}).get("object", {})

    handled = False
    if event_type == "checkout.session.completed":
        handled = _handle_checkout_completed(data)
    elif event_type in {"invoice.paid", "invoice.payment_succeeded"}:
        handled = _handle_invoice_paid(data)
    elif event_type == "invoice.payment_failed":
        handled = _handle_invoice_failed(data)
    elif event_type in {"customer.subscription.deleted", "customer.subscription.cancelled"}:
        handled = _handle_subscription_cancelled(data)
    elif event_type == "customer.subscription.updated":
        handled = _handle_subscription_updated(data)

    if handled:
        db.session.commit()
    else:
        db.session.rollback()
    return jsonify({"handled": handled})


def _handle_checkout_completed(session: Dict[str, Any]) -> bool:
    user = _find_user_by_stripe(
        user_id=(session.get("metadata") or {}).get("user_id"),
        customer_id=session.get("customer"),
        email=((session.get("customer_details") or {}).get("email")),
    )
    if not user:
        return False

    customer_details = session.get("customer_details") or {}
    address = customer_details.get("address") or {}

    user.stripe_customer_id = session.get("customer") or user.stripe_customer_id
    user.stripe_subscription_id = session.get("subscription") or user.stripe_subscription_id
    user.plan = "pro"
    user.plan_started_at = datetime.utcnow()

    user.billing_name = customer_details.get("name") or user.billing_name or user.name
    user.billing_address_line1 = address.get("line1") or user.billing_address_line1
    user.billing_address_line2 = address.get("line2") or user.billing_address_line2
    user.billing_postal_code = address.get("postal_code") or user.billing_postal_code
    user.billing_city = address.get("city") or user.billing_city
    user.billing_region = address.get("state") or user.billing_region
    user.billing_country = (address.get("country") or user.billing_country or "").upper() or None
    user.billing_tax_id = None
    tax_ids = customer_details.get("tax_ids") or []
    if tax_ids:
        user.billing_tax_id = tax_ids[0].get("value") or user.billing_tax_id

    metadata = user.plan_metadata or {}
    metadata["stripe"] = {
        "customer_id": user.stripe_customer_id,
        "subscription_id": user.stripe_subscription_id,
        "checkout_session": session.get("id"),
    }
    user.plan_metadata = metadata

    return True


def _handle_invoice_paid(invoice: Dict[str, Any]) -> bool:
    customer_id = invoice.get("customer")
    user = _find_user_by_stripe(customer_id=customer_id)
    if not user:
        return False

    amount_paid = Decimal(invoice.get("amount_paid", 0)) / Decimal(100)
    tax_amount = Decimal(invoice.get("tax", 0)) / Decimal(100)
    net_amount = amount_paid - tax_amount
    currency = (invoice.get("currency") or "eur").upper()
    invoice_id = invoice.get("id")

    payment = Payment.query.filter_by(order_id=invoice_id).first()
    if payment is None:
        payment = Payment(
            user_id=user.id,
            processor="stripe",
            order_id=invoice_id,
            status=invoice.get("status", "paid").upper(),
            amount=amount_paid,
            net_amount=net_amount,
            tax_amount=tax_amount,
            currency=currency,
            metadata={"stripe": invoice},
        )
        db.session.add(payment)
    else:
        payment.status = invoice.get("status", payment.status)
        payment.amount = amount_paid
        payment.net_amount = net_amount
        payment.tax_amount = tax_amount
        payment.currency = currency
        metadata = payment.metadata or {}
        metadata["stripe"] = invoice
        payment.metadata = metadata

    payment.payer_email = ((invoice.get("customer_email") or user.email) or None)
    payment.invoice_number = invoice.get("number") or payment.invoice_number
    payment.invoice_path = invoice.get("hosted_invoice_url") or payment.invoice_path
    payment.updated_at = datetime.utcnow()

    # Ensure subscription remains active
    user.plan = "pro"
    user.plan_started_at = datetime.utcnow()
    meta = user.plan_metadata or {}
    meta.setdefault("stripe", {})["latest_invoice"] = invoice_id
    user.plan_metadata = meta
    return True


def _handle_invoice_failed(invoice: Dict[str, Any]) -> bool:
    customer_id = invoice.get("customer")
    user = _find_user_by_stripe(customer_id=customer_id)
    if not user:
        return False
    meta = user.plan_metadata or {}
    meta.setdefault("stripe", {})["payment_failed_at"] = datetime.utcnow().isoformat() + "Z"
    user.plan_metadata = meta
    return True


def _handle_subscription_cancelled(subscription: Dict[str, Any]) -> bool:
    subscription_id = subscription.get("id")
    user = None
    if subscription_id:
        user = User.query.filter_by(stripe_subscription_id=subscription_id).first()
    if not user:
        return False
    user.plan = "trial_expired"
    meta = user.plan_metadata or {}
    meta.setdefault("stripe", {})["subscription_status"] = subscription.get("status")
    meta["stripe"]["ended_at"] = datetime.utcnow().isoformat() + "Z"
    user.plan_metadata = meta
    return True


def _handle_subscription_updated(subscription: Dict[str, Any]) -> bool:
    subscription_id = subscription.get("id")
    if not subscription_id:
        return False
    user = User.query.filter_by(stripe_subscription_id=subscription_id).first()
    if not user:
        return False
    status = subscription.get("status")
    meta = user.plan_metadata or {}
    meta.setdefault("stripe", {})["subscription_status"] = status
    user.plan_metadata = meta
    if status in {"active", "trialing", "past_due"}:
        user.plan = "pro"
    elif status in {"canceled", "unpaid"}:
        user.plan = "trial_expired"
    return True
