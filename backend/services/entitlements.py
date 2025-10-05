from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from flask import Request

from ..models import User

TIER_SIDEBAR_GROUPS: Dict[str, List[str]] = {
    "free": ["search"],
    "pro": ["search", "marketplaces", "social", "video"],
    "enterprise": ["search", "marketplaces", "social", "video", "enterprise"],
}


@dataclass(frozen=True)
class Entitlements:
    tier: str
    ai_credits: int
    sidebar_groups: List[str]
    upgrade_url: str
    buy_credits_url: str
    expires_at: Optional[str]

    def to_dict(self) -> Dict[str, object]:
        payload: Dict[str, object] = {
            "tier": self.tier,
            "ai_credits": self.ai_credits,
            "sidebar_groups": self.sidebar_groups,
            "upgrade_url": self.upgrade_url,
            "buy_credits_url": self.buy_credits_url,
        }
        if self.expires_at:
            payload["expires_at"] = self.expires_at
        return payload


def _base_url(request: Request) -> str:
    configured = (os.getenv("PUBLIC_BASE_URL") or "").strip()
    if configured:
        return configured.rstrip("/")
    root = (request.url_root or "").strip()
    return root.rstrip("/") if root else "http://localhost:5000"


def _normalize_tier(user: Optional[User]) -> str:
    if user is None:
        return "free"
    metadata = user.plan_metadata or {}
    tier = (metadata.get("tier") or "").strip().lower()
    if tier in {"free", "pro", "enterprise"}:
        return tier
    plan = (user.plan or "").strip().lower()
    if plan in {"pro", "enterprise"}:
        return plan
    return "free"


def _ai_credits(user: Optional[User]) -> int:
    if user is None:
        return 0
    metadata = user.plan_metadata or {}
    raw_value = metadata.get("ai_credits", 0)
    try:
        credits = int(raw_value)
    except (TypeError, ValueError):
        credits = 0
    return max(credits, 0)


def _expires_at(user: Optional[User]) -> Optional[str]:
    if user is None:
        return None
    metadata = user.plan_metadata or {}
    expires_raw = metadata.get("expires_at")
    if not expires_raw:
        return None
    if isinstance(expires_raw, str):
        return expires_raw
    if isinstance(expires_raw, datetime):
        return expires_raw.replace(microsecond=0).isoformat() + "Z"
    return None


def _sidebar_groups_for(tier: str, ai_credits: int) -> List[str]:
    groups = list(TIER_SIDEBAR_GROUPS.get(tier, TIER_SIDEBAR_GROUPS["free"]))
    if ai_credits > 0 and "ai" not in groups:
        groups.append("ai")
    return groups


def build_entitlements(user: Optional[User], request: Request) -> Entitlements:
    tier = _normalize_tier(user)
    credits = _ai_credits(user)
    groups = _sidebar_groups_for(tier, credits)
    base_url = _base_url(request)

    upgrade_url = os.getenv("ENTITLEMENTS_UPGRADE_URL") or f"{base_url}/billing/upgrade"
    buy_credits_url = os.getenv("ENTITLEMENTS_BUY_CREDITS_URL") or f"{base_url}/billing/credits"

    expires_at = _expires_at(user)

    return Entitlements(
        tier=tier,
        ai_credits=credits,
        sidebar_groups=groups,
        upgrade_url=upgrade_url,
        buy_credits_url=buy_credits_url,
        expires_at=expires_at,
    )
