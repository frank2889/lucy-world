#!/usr/bin/env python3
"""Smoke-test the public /meta endpoints using the Flask test client."""
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
class SmokeCase:
    path: str
    kind: str  # "json" or "xml"
    validator: Optional[Callable[[object], tuple[bool, str] | bool]] = None


def _json_validator(required_keys: set[str]) -> Callable[[object], tuple[bool, str]]:
    def _inner(payload: object) -> tuple[bool, str]:
        if not isinstance(payload, dict):
            return False, f"Expected object, got {type(payload).__name__}"
        missing = [key for key in required_keys if not payload.get(key)]
        if missing:
            return False, f"Missing keys: {', '.join(missing)}"
        return True, "OK"

    return _inner


def run() -> int:
    app = create_app()
    client = app.test_client()

    cases: list[SmokeCase] = [
        SmokeCase("/meta/detect.json", "json", _json_validator({"language", "country"})),
        SmokeCase("/meta/languages.json", "json", _json_validator({"languages"})),
        SmokeCase("/meta/locales.json", "json", _json_validator({"locales", "default"})),
        SmokeCase("/meta/countries.json", "json", _json_validator({"countries"})),
        SmokeCase("/meta/markets.json", "json", _json_validator({"markets"})),
        SmokeCase("/meta/sitemap.xml", "xml"),
    ]

    failures: list[str] = []

    for case in cases:
        response = client.get(case.path)
        if response.status_code != 200:
            failures.append(f"{case.path}: unexpected status {response.status_code}")
            continue

        if case.kind == "json":
            try:
                payload = response.get_json()
            except Exception as exc:  # pragma: no cover - defensive
                failures.append(f"{case.path}: invalid JSON ({exc})")
                continue
            if case.validator:
                verdict = case.validator(payload)
                if isinstance(verdict, tuple):
                    ok, message = verdict
                else:
                    ok, message = bool(verdict), ""
                if not ok:
                    failures.append(f"{case.path}: {message or 'validation failed'}")
        elif case.kind == "xml":
            content_type = response.headers.get("Content-Type", "")
            if "xml" not in content_type:
                failures.append(f"{case.path}: unexpected content type {content_type!r}")
        else:  # pragma: no cover - defensive guard for future kinds
            failures.append(f"{case.path}: unknown case type {case.kind}")

    if failures:
        for line in failures:
            print(f"❌ {line}")
        print(f"{len(failures)} smoke check(s) failed.")
        return 1

    print("✅ All /meta endpoints responded successfully.")
    return 0


def main() -> int:
    try:
        return run()
    except Exception as exc:  # pragma: no cover - defensive
        print(f"❌ Smoke tests crashed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
