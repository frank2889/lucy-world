#!/usr/bin/env python3
"""Operational health probe for the Lucy World Gunicorn service.

This script is intended to run on the production server (for example via
cron, systemd timers, or a CI smoke test) to assert that the Gunicorn service
is healthy and that the public health endpoints respond quickly.

Success criteria:
  1. The configured systemd service is active (if systemd is available).
  2. The `/meta/detect.json` endpoint responds with HTTP 200 and valid JSON.
  3. The `/api/free/search` endpoint responds to a test POST with HTTP 200.

It prints a JSON summary to STDOUT and exits with a non-zero status code if any
check fails, making it suitable for integration with monitoring pipelines.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from typing import Any, Dict, List

import requests

DEFAULT_BASE_URL = "https://lucy.world"
DEFAULT_SERVICE_NAME = "lucy-world-search"


class CheckError(RuntimeError):
    """Raised when a health check fails."""


def run_systemctl_checks(service_name: str) -> Dict[str, Any]:
    """Return status information for a systemd service.

    When `systemctl` is unavailable (e.g., running locally on macOS), the
    check is skipped but noted in the output instead of failing hard.
    """

    systemctl_path = shutil.which("systemctl")
    if systemctl_path is None:
        return {
            "service": service_name,
            "systemctl_available": False,
            "status": "unknown",
            "detail": "systemctl not available on this host",
        }

    result = {
        "service": service_name,
        "systemctl_available": True,
        "status": "unknown",
        "detail": "",
    }

    try:
        status_proc = subprocess.run(
            [systemctl_path, "is-active", service_name],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        status_output = status_proc.stdout.strip() or status_proc.stderr.strip()
        result["status"] = status_output or "unknown"
        result["returncode"] = status_proc.returncode
        if status_proc.returncode != 0:
            raise CheckError(
                f"systemctl reports service '{service_name}' as '{status_output or 'inactive'}'"
            )
    except subprocess.TimeoutExpired as exc:  # pragma: no cover - defensive
        raise CheckError(f"systemctl timed out while checking '{service_name}'") from exc

    try:
        detail_proc = subprocess.run(
            [systemctl_path, "show", service_name, "--property=SubState", "--value"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        result["substate"] = detail_proc.stdout.strip()
    except subprocess.TimeoutExpired:
        # If the detail call times out we simply omit the field.
        pass

    return result


def http_get_json(url: str, timeout: float = 10.0) -> Dict[str, Any]:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    try:
        return response.json()
    except ValueError as exc:
        raise CheckError(f"Endpoint {url} did not return valid JSON") from exc


def http_post_json(url: str, payload: Dict[str, Any], timeout: float = 10.0) -> Dict[str, Any]:
    response = requests.post(url, json=payload, timeout=timeout)
    response.raise_for_status()
    try:
        return response.json()
    except ValueError as exc:
        raise CheckError(f"Endpoint {url} did not return valid JSON") from exc


def run_http_checks(
    base_url: str,
    keyword: str,
    language: str,
    country: str | None,
    timeout: float,
) -> Dict[str, Any]:
    detect_url = base_url.rstrip("/") + "/meta/detect.json"
    free_search_url = base_url.rstrip("/") + "/api/free/search"

    detect_started = time.perf_counter()
    detect_payload = http_get_json(detect_url, timeout=timeout)
    detect_duration = time.perf_counter() - detect_started

    free_payload_template = {
        "keyword": keyword,
        "language": language,
    }
    if country:
        free_payload_template["country"] = country

    free_started = time.perf_counter()
    free_payload = http_post_json(free_search_url, free_payload_template, timeout=timeout)
    free_duration = time.perf_counter() - free_started

    return {
        "detect": {
            "url": detect_url,
            "status": 200,
            "duration_ms": round(detect_duration * 1000, 2),
            "payload_sample": detect_payload,
        },
        "free_search": {
            "url": free_search_url,
            "status": 200,
            "duration_ms": round(free_duration * 1000, 2),
            "request": free_payload_template,
            "payload_sample": {
                "language": free_payload.get("language"),
                "providers": len(free_payload.get("providers", [])),
                "unique_suggestions": free_payload.get("metadata", {}).get("unique_suggestions"),
            },
        },
    }


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"Public base URL to probe (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--service",
        default=DEFAULT_SERVICE_NAME,
        help=f"systemd service name to verify (default: {DEFAULT_SERVICE_NAME})",
    )
    parser.add_argument(
        "--keyword",
        default="lucy world",
        help="Keyword to use for the free search smoke test",
    )
    parser.add_argument(
        "--language",
        default="en",
        help="ISO 639-1 language code for the free search smoke test",
    )
    parser.add_argument(
        "--country",
        default=None,
        help="Optional ISO 3166-1 alpha-2 country code for the free search smoke test",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="HTTP timeout in seconds (default: 10)",
    )
    return parser.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    report: Dict[str, Any] = {
        "base_url": args.base_url,
        "service": args.service,
        "timestamp": int(time.time()),
        "checks": {},
    }

    try:
        report["checks"]["systemd"] = run_systemctl_checks(args.service)
        report["checks"]["http"] = run_http_checks(
            base_url=args.base_url,
            keyword=args.keyword,
            language=args.language,
            country=args.country,
            timeout=args.timeout,
        )
    except (requests.RequestException, CheckError) as exc:
        report["error"] = str(exc)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
