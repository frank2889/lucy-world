#!/usr/bin/env python3
"""Smoke-test public API endpoints for the Lucy World backend."""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend import create_app  # noqa: E402


@dataclass
class SmokeResult:
    name: str
    ok: bool
    details: str = ""


def _ensure(condition: bool, message: str) -> tuple[bool, str]:
    return (condition, "OK" if condition else message)


def _test_meta_content(client) -> SmokeResult:
    response = client.get("/meta/content/en.json")
    if response.status_code != 200:
        return SmokeResult("meta-content", False, f"unexpected status {response.status_code}")
    try:
        payload = response.get_json()
    except Exception as exc:  # pragma: no cover - defensive
        return SmokeResult("meta-content", False, f"invalid JSON: {exc}")

    ok, message = _ensure(isinstance(payload, dict) and isinstance(payload.get("strings"), dict),
                          "missing strings block")
    if not ok:
        return SmokeResult("meta-content", False, message)
    required_keys = {"meta.title", "meta.description", "meta.keywords"}
    strings = payload["strings"]
    missing = sorted(k for k in required_keys if not strings.get(k))
    if missing:
        return SmokeResult("meta-content", False, f"missing meta keys: {', '.join(missing)}")
    return SmokeResult("meta-content", True)


def _test_premium_search(client) -> list[SmokeResult]:
    results: list[SmokeResult] = []

    # Happy path
    response = client.post("/api/premium/search", json={
        "keyword": "coffee",
        "language": "en",
        "country": "US",
    })
    if response.status_code != 200:
        results.append(SmokeResult("premium-search:happy", False, f"unexpected status {response.status_code}"))
    else:
        try:
            payload = response.get_json()
        except Exception as exc:  # pragma: no cover - defensive
            results.append(SmokeResult("premium-search:happy", False, f"invalid JSON: {exc}"))
        else:
            checks = [
                _ensure(isinstance(payload, dict), "payload not object"),
                _ensure(payload.get("keyword") == "coffee", "keyword mismatch"),
                _ensure(isinstance(payload.get("categories"), dict), "categories missing"),
                _ensure("summary" in payload, "summary missing"),
            ]
            failing = [msg for ok, msg in checks if not ok]
            if failing:
                results.append(SmokeResult("premium-search:happy", False, "; ".join(failing)))
            else:
                results.append(SmokeResult("premium-search:happy", True))

    # Validation path (missing keyword)
    response = client.post("/api/premium/search", json={})
    if response.status_code != 400:
        results.append(SmokeResult("premium-search:missing-keyword", False, f"expected 400, got {response.status_code}"))
    else:
        try:
            payload = response.get_json()
        except Exception as exc:  # pragma: no cover - defensive
            results.append(SmokeResult("premium-search:missing-keyword", False, f"invalid JSON: {exc}"))
        else:
            if not isinstance(payload, dict) or "error" not in payload:
                results.append(SmokeResult("premium-search:missing-keyword", False, "no error message"))
            else:
                results.append(SmokeResult("premium-search:missing-keyword", True))

    return results


def run() -> int:
    app = create_app()
    client = app.test_client()

    outcomes: list[SmokeResult] = []
    outcomes.append(_test_meta_content(client))
    outcomes.extend(_test_premium_search(client))

    failures = [res for res in outcomes if not res.ok]
    if failures:
        for res in failures:
            print(f"❌ {res.name}: {res.details}")
        print(f"{len(failures)} public API smoke check(s) failed.")
        return 1

    print("✅ Public API smoke tests passed.")
    return 0


def main() -> int:
    try:
        return run()
    except Exception as exc:  # pragma: no cover - defensive
        print(f"❌ Smoke tests crashed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
