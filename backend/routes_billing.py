from __future__ import annotations

import json
import secrets
import os
from decimal import Decimal
from typing import Any, Dict, List, Optional

import stripe  # type: ignore
from flask import Blueprint, current_app, jsonify, request

from .extensions import db
from .models import Payment, User
from .routes_helpers import auth_required, get_current_user
from .services.credits import ensure_plan_metadata, grant_ai_credits
from .utils import from_timestamp_utc, structured_log, to_utc_isoformat, utcnow

bp = Blueprint("billing", __name__, url_prefix="/api/billing")


class StripeConfigurationError(RuntimeError):
    """Raised when Stripe is not configured correctly."""


def _ensure_customer(user: User) -> str:
    _ensure_stripe_api()
    customer_id = (user.stripe_customer_id or "").strip()
    if customer_id:
        try:
            stripe.Customer.modify(customer_id, metadata={"user_id": str(user.id)})
        except Exception as exc:  # pragma: no cover - defensive
            current_app.logger.warning("Stripe customer modify failed for %s: %s", user.email, exc)
        return customer_id

    try:
        customer = stripe.Customer.create(
            email=user.email,
            name=user.name or user.email,
            metadata={"user_id": str(user.id)},
        )
    except Exception as exc:  # pragma: no cover - Stripe runtime failures
        raise StripeConfigurationError(f"Unable to create Stripe customer: {exc}") from exc

    user.stripe_customer_id = customer.id
    db.session.commit()
    return customer.id


def _set_subscription_expiry(meta: Dict[str, Any], period_end: Any) -> None:
    if isinstance(period_end, (int, float)):
        meta["expires_at"] = to_utc_isoformat(from_timestamp_utc(period_end))
    elif isinstance(period_end, str):
        meta["expires_at"] = period_end
    else:
        meta.pop("expires_at", None)



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


def _credit_catalog() -> List[Dict[str, Any]]:
    """Return configured credit packs augmented with Stripe price metadata."""
    raw = (os.getenv("STRIPE_CREDIT_PACKS") or "").strip()
    packs: List[Dict[str, Any]] = []

    if raw:
        try:
            data = json.loads(raw)
        except Exception as exc:  # pragma: no cover - invalid JSON caught during deploy
            current_app.logger.error("Invalid STRIPE_CREDIT_PACKS JSON: %s", exc)
            data = []
        if isinstance(data, list):
            packs.extend([entry for entry in data if isinstance(entry, dict)])

    if not packs:
        # Fallback to usage-based billing configuration when dedicated packs are unset
        usage_price = (os.getenv("STRIPE_PRICE_PRO_USAGE") or "").strip()
        credits_per_unit_env = os.getenv("STRIPE_AI_CREDITS_PER_UNIT") or "100"
        try:
            credits_per_unit = max(int(credits_per_unit_env), 0)
        except ValueError:
            credits_per_unit = 0
        if usage_price and credits_per_unit:
            packs.append(
                {
                    "price_id": usage_price,
                    "credits": credits_per_unit,
                    "nickname": "AI credit pack",
                    "mode": "usage",
                }
            )

    if not packs:
        return []

    enriched: List[Dict[str, Any]] = []
    try:
        _ensure_stripe_api()
    except StripeConfigurationError as exc:
        current_app.logger.warning("Stripe not configured for credit packs: %s", exc)
        for entry in packs:
            enriched.append({
                "price_id": entry.get("price_id"),
                "credits": entry.get("credits", 0),
                "currency": entry.get("currency", ""),
                "unit_amount": entry.get("amount") or entry.get("unit_amount"),
                "nickname": entry.get("nickname") or entry.get("name"),
                "mode": entry.get("mode", "payment"),
                "description": entry.get("description"),
            })
        return enriched

    for entry in packs:
        price_id = (entry.get("price_id") or "").strip()
        if not price_id:
            continue
        try:
            price = stripe.Price.retrieve(price_id, expand=["product"])  # type: ignore[arg-type]
        except Exception as exc:  # pragma: no cover - Stripe runtime
            current_app.logger.error("Unable to load Stripe price %s: %s", price_id, exc)
            continue
        product = price.get("product")
        nickname = entry.get("nickname") or entry.get("name")
        if not nickname and isinstance(product, dict):
            nickname = product.get("name") or product.get("metadata", {}).get("display_name")
        enriched.append(
            {
                "price_id": price_id,
                "credits": int(entry.get("credits") or 0),
                "currency": (price.get("currency") or entry.get("currency") or "").upper(),
                "unit_amount": price.get("unit_amount") or entry.get("amount") or entry.get("unit_amount"),
                "nickname": nickname or price.get("nickname") or "AI credit pack",
                "mode": entry.get("mode", "payment"),
                "description": entry.get("description") or (isinstance(product, dict) and product.get("description")),
            }
        )

    enriched.sort(key=lambda item: item.get("credits") or 0)
    return enriched


def _find_user_by_stripe(
    *,
    user_id: Optional[str] = None,
    customer_id: Optional[str] = None,
    email: Optional[str] = None,
) -> Optional[User]:
    user: Optional[User] = None
    if user_id:
        try:
            user = db.session.get(User, int(user_id))
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
        price_ids = _price_ids()
    except StripeConfigurationError as exc:
        return jsonify({"error": str(exc)}), 500

    try:
        customer_id = _ensure_customer(user)
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


@bp.route("/credit-checkout", methods=["POST"])
@auth_required
def create_credit_checkout_session() -> Any:
    payload = request.get_json(silent=True) or {}
    price_id = (payload.get("price_id") or "").strip()
    if not price_id:
        return jsonify({"error": "price_id_required"}), 400

    packs = _credit_catalog()
    pack = next((p for p in packs if p.get("price_id") == price_id), None)
    if not pack:
        return jsonify({"error": "unknown_price"}), 400

    user = get_current_user()

    try:
        customer_id = _ensure_customer(user)
    except StripeConfigurationError as exc:
        current_app.logger.error("Credit checkout failed (customer): %s", exc)
        return jsonify({"error": "stripe_not_configured"}), 500

    base_url = _public_base_url()
    success_url = f"{base_url}/billing/credits?status=success"
    cancel_url = f"{base_url}/billing/credits?status=cancelled"

    try:
        session = stripe.checkout.Session.create(  # type: ignore[call-arg]
            mode="payment",
            customer=customer_id,
            line_items=[
                {
                    "price": price_id,
                    "quantity": int(payload.get("quantity") or 1),
                }
            ],
            success_url=success_url + "&session_id={CHECKOUT_SESSION_ID}",
            cancel_url=cancel_url,
            automatic_tax={"enabled": True},
            metadata={
                "user_id": str(user.id),
                "type": "credit_pack",
                "credits": str(pack.get("credits") or 0),
                "price_id": price_id,
            },
        )
    except Exception as exc:  # pragma: no cover - Stripe runtime failures
        current_app.logger.error("Failed to create credit checkout session: %s", exc)
        return jsonify({"error": "unable_to_create_session"}), 502

    return jsonify({"url": session.url})


@bp.route("/credit-packs", methods=["GET"])
@auth_required
def list_credit_packs() -> Any:
    packs = _credit_catalog()
    return jsonify({"packs": packs, "count": len(packs)})


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

    mode = session.get("mode") or "subscription"
    metadata = session.get("metadata") or {}

    if mode == "payment" and metadata.get("type") == "credit_pack":
        credits_raw = metadata.get("credits")
        try:
            credits = max(int(credits_raw or 0), 0)
        except (TypeError, ValueError):
            credits = 0
        if credits <= 0:
            current_app.logger.warning("Credit checkout completed without positive credits: %s", session.get("id"))
            return True

        grant_ai_credits(
            user,
            credits,
            source="stripe_credit_checkout",
            reference=session.get("id"),
        )

        amount_total = Decimal(session.get("amount_total", 0) or 0) / Decimal(100)
        currency = (session.get("currency") or "usd").upper()
        payment = Payment.query.filter_by(order_id=session.get("id") or "").first()
        if payment is None:
            payment = Payment(
                user_id=user.id,
                processor="stripe",
                order_id=session.get("id") or secrets.token_urlsafe(16),
                status=session.get("payment_status", "completed").upper(),
                amount=amount_total,
                net_amount=amount_total,
                tax_amount=Decimal("0"),
                currency=currency,
                payer_email=session.get("customer_details", {}).get("email") or user.email,
                metadata_payload={"stripe": session},
            )
            db.session.add(payment)
        else:
            payment.status = session.get("payment_status", payment.status)
            payment.amount = amount_total
            payment.net_amount = amount_total
            payment.currency = currency
            payment.metadata_payload = {"stripe": session}

        ensure_plan_metadata(user)
        structured_log(
            "entitlement_change",
            action="credit_pack_purchase",
            user_id=user.id,
            credits=credits,
            checkout_session=session.get("id"),
            amount=float(amount_total),
            currency=currency,
        )
        return True

    customer_details = session.get("customer_details") or {}
    address = customer_details.get("address") or {}

    user.stripe_customer_id = session.get("customer") or user.stripe_customer_id
    user.stripe_subscription_id = session.get("subscription") or user.stripe_subscription_id
    user.plan = "pro"
    user.plan_started_at = utcnow()

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

    metadata = ensure_plan_metadata(user)
    metadata["tier"] = "pro"
    metadata["stripe"] = {
        "customer_id": user.stripe_customer_id,
        "subscription_id": user.stripe_subscription_id,
        "checkout_session": session.get("id"),
    }
    _set_subscription_expiry(metadata, session.get("subscription") and session.get("expires_at"))
    user.plan_metadata = metadata

    structured_log(
        "entitlement_change",
        action="upgrade_to_pro",
        user_id=user.id,
        stripe_customer_id=user.stripe_customer_id,
        stripe_subscription_id=user.stripe_subscription_id,
        checkout_session=session.get("id"),
    )

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
            metadata_payload={"stripe": invoice},
        )
        db.session.add(payment)
    else:
        payment.status = invoice.get("status", payment.status)
        payment.amount = amount_paid
        payment.net_amount = net_amount
        payment.tax_amount = tax_amount
        payment.currency = currency
        metadata = dict(payment.metadata_payload or {})
        metadata["stripe"] = invoice
        payment.metadata_payload = metadata

    payment.payer_email = ((invoice.get("customer_email") or user.email) or None)
    payment.invoice_number = invoice.get("number") or payment.invoice_number
    payment.invoice_path = invoice.get("hosted_invoice_url") or payment.invoice_path
    payment.updated_at = utcnow()

    # Ensure subscription remains active
    user.plan = "pro"
    user.plan_started_at = utcnow()
    meta = ensure_plan_metadata(user)
    meta.setdefault("stripe", {})["latest_invoice"] = invoice_id
    meta["tier"] = "pro"
    period_end = (invoice.get("lines", {}).get("data", [{}])[0].get("period") or {}).get("end")
    _set_subscription_expiry(meta, period_end)
    user.plan_metadata = meta

    usage_price_id = (os.getenv("STRIPE_PRICE_PRO_USAGE") or "").strip()
    credits_per_unit_env = os.getenv("STRIPE_AI_CREDITS_PER_UNIT") or "100"
    try:
        credits_per_unit = max(int(credits_per_unit_env), 0)
    except ValueError:
        credits_per_unit = 0

    if usage_price_id and credits_per_unit > 0:
        purchased_units = 0
        for line in invoice.get("lines", {}).get("data", []):
            price_info = line.get("price")
            if isinstance(price_info, dict):
                price_id = price_info.get("id") or ""
            else:
                price_id = price_info or ""
            if price_id != usage_price_id:
                continue
            quantity = line.get("quantity")
            if quantity is None:
                quantity = line.get("usage")
            try:
                units = int(quantity or 0)
            except (TypeError, ValueError):
                units = 0
            if units > 0:
                purchased_units += units
        if purchased_units > 0:
            grant_ai_credits(
                user,
                purchased_units * credits_per_unit,
                source="stripe_invoice",
                reference=invoice_id,
            )
    structured_log(
        "entitlement_change",
        action="invoice_paid",
        user_id=user.id,
        invoice_id=invoice_id,
        plan=user.plan,
        ai_credits=user.plan_metadata.get("ai_credits") if isinstance(user.plan_metadata, dict) else None,
    )
    return True


def _handle_invoice_failed(invoice: Dict[str, Any]) -> bool:
    customer_id = invoice.get("customer")
    user = _find_user_by_stripe(customer_id=customer_id)
    if not user:
        return False
    meta = ensure_plan_metadata(user)
    meta.setdefault("stripe", {})["payment_failed_at"] = to_utc_isoformat()
    user.plan_metadata = meta
    structured_log(
        "entitlement_change",
        action="invoice_failed",
        user_id=user.id,
        invoice_id=invoice.get("id"),
        plan=user.plan,
    )
    return True


def _handle_subscription_cancelled(subscription: Dict[str, Any]) -> bool:
    subscription_id = subscription.get("id")
    user = None
    if subscription_id:
        user = User.query.filter_by(stripe_subscription_id=subscription_id).first()
    if not user:
        return False
    user.plan = "trial_expired"
    meta = ensure_plan_metadata(user)
    meta.setdefault("stripe", {})["subscription_status"] = subscription.get("status")
    meta["stripe"]["ended_at"] = to_utc_isoformat()
    meta["tier"] = "free"
    meta.pop("expires_at", None)
    user.plan_metadata = meta
    structured_log(
        "entitlement_change",
        action="subscription_cancelled",
        user_id=user.id,
        stripe_subscription_id=subscription_id,
        plan=user.plan,
    )
    return True


def _handle_subscription_updated(subscription: Dict[str, Any]) -> bool:
    subscription_id = subscription.get("id")
    if not subscription_id:
        return False
    user = User.query.filter_by(stripe_subscription_id=subscription_id).first()
    if not user:
        return False
    status = subscription.get("status")
    meta = ensure_plan_metadata(user)
    meta.setdefault("stripe", {})["subscription_status"] = status
    period = subscription.get("current_period_end")
    _set_subscription_expiry(meta, period)
    user.plan_metadata = meta
    if status in {"active", "trialing", "past_due"}:
        user.plan = "pro"
        meta["tier"] = "pro"
    elif status in {"canceled", "unpaid"}:
        user.plan = "trial_expired"
        meta["tier"] = "free"
        meta.pop("expires_at", None)
    structured_log(
        "entitlement_change",
        action="subscription_updated",
        user_id=user.id,
        stripe_subscription_id=subscription_id,
        status=status,
        plan=user.plan,
    )
    return True
