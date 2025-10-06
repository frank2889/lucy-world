from __future__ import annotations

from typing import Any, Optional

from ..models import User
from ..utils import structured_log, to_utc_isoformat

_MAX_HISTORY = 20


def ensure_plan_metadata(user: User) -> dict[str, Any]:
    raw_meta = user.plan_metadata if isinstance(user.plan_metadata, dict) else {}
    meta: dict[str, Any] = dict(raw_meta or {})
    if "tier" not in meta or not isinstance(meta.get("tier"), str):
        meta["tier"] = "free"
    if "ai_credits" not in meta:
        meta["ai_credits"] = 0
    user.plan_metadata = meta
    return meta


def _coerce_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _append_event(meta: dict[str, Any], event: dict[str, Any]) -> None:
    events = list(meta.get("credit_events") or [])
    events.append(event)
    meta["credit_events"] = events[-_MAX_HISTORY:]


def grant_ai_credits(
    user: User,
    amount: int,
    *,
    source: Optional[str] = None,
    reference: Optional[str] = None,
) -> int:
    meta = ensure_plan_metadata(user)
    amount_value = max(_coerce_int(amount), 0)
    balance = _coerce_int(meta.get("ai_credits"))
    new_balance = balance + amount_value
    meta["ai_credits"] = new_balance
    if amount_value > 0:
        _append_event(
            meta,
            {
                "type": "grant",
                "amount": amount_value,
                "source": source,
                "reference": reference,
                "at": to_utc_isoformat(),
            },
        )
        structured_log(
            "entitlement_change",
            action="grant_ai_credits",
            user_id=user.id,
            amount=amount_value,
            new_balance=new_balance,
            source=source,
            reference=reference,
        )
    user.plan_metadata = meta
    return new_balance


def consume_ai_credit(
    user: User,
    amount: int = 1,
    *,
    reason: Optional[str] = None,
) -> int:
    meta = ensure_plan_metadata(user)
    amount_value = max(_coerce_int(amount), 0)
    if amount_value == 0:
        return _coerce_int(meta.get("ai_credits"))
    balance = _coerce_int(meta.get("ai_credits"))
    new_balance = max(balance - amount_value, 0)
    meta["ai_credits"] = new_balance
    _append_event(
        meta,
        {
            "type": "consume",
            "amount": amount_value,
            "reason": reason,
            "at": to_utc_isoformat(),
        },
    )
    structured_log(
        "ai_credit_consumed",
        user_id=user.id,
        amount=amount_value,
        new_balance=new_balance,
        reason=reason,
    )
    user.plan_metadata = meta
    return new_balance


__all__ = [
    "ensure_plan_metadata",
    "grant_ai_credits",
    "consume_ai_credit",
]
