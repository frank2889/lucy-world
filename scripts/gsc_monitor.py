#!/usr/bin/env python3
"""Monitor Google Search Console metrics for Lucy World Search (service account edition)."""

from __future__ import annotations

import argparse
import datetime as dt
import os
import sys
import textwrap
from typing import Any, Dict, List

from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

DEFAULT_PROPERTY = "sc-domain:lucy.world"
DEFAULT_INSPECTION_URL = "https://lucy.world/"
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
SERVICE_ACCOUNT_ENV_MAP = {
    "GSC_TYPE": "type",
    "GSC_PROJECT_ID": "project_id",
    "GSC_PRIVATE_KEY_ID": "private_key_id",
    "GSC_PRIVATE_KEY": "private_key",
    "GSC_CLIENT_EMAIL": "client_email",
    "GSC_CLIENT_ID": "client_id",
    "GSC_AUTH_URI": "auth_uri",
    "GSC_TOKEN_URI": "token_uri",
    "GSC_AUTH_PROVIDER_CERT_URL": "auth_provider_x509_cert_url",
    "GSC_CLIENT_CERT_URL": "client_x509_cert_url",
    "GSC_UNIVERSE_DOMAIN": "universe_domain",
}


class GSCMonitorError(RuntimeError):
    """Raised when Search Console data cannot be retrieved."""


def _load_credentials() -> service_account.Credentials:
    load_dotenv()
    key_path = (os.getenv("GSC_SERVICE_ACCOUNT_FILE") or "").strip()
    if key_path:
        if not os.path.exists(key_path):
            raise GSCMonitorError(f"❌ Service account file not found: {key_path}")
        try:
            return service_account.Credentials.from_service_account_file(
                key_path,
                scopes=SCOPES,
            )
        except ValueError as exc:
            raise GSCMonitorError(
                f"❌ Failed to load service account credentials: {exc}"
            ) from exc

    env_info: Dict[str, str] = {}
    missing_env = []
    for env_key, info_key in SERVICE_ACCOUNT_ENV_MAP.items():
        value = os.getenv(env_key)
        if not value:
            missing_env.append(env_key)
            continue
        if info_key == "private_key":
            value = value.replace("\\n", "\n")
        env_info[info_key] = value

    if not missing_env:
        try:
            return service_account.Credentials.from_service_account_info(
                env_info,
                scopes=SCOPES,
            )
        except ValueError as exc:
            raise GSCMonitorError(
                f"❌ Failed to load service account credentials from environment: {exc}"
            ) from exc

    missing = ", ".join(missing_env)
    message = textwrap.dedent(
        f"""
        ❌ Missing Search Console service account credentials. Set GSC_SERVICE_ACCOUNT_FILE
        to a JSON key path or define all of the following variables in the environment:
        {missing}.
        """
    ).strip()
    raise GSCMonitorError(message)


def _build_service(creds):
    try:
        return build("searchconsole", "v1", credentials=creds, cache_discovery=False)
    except Exception as exc:  # pragma: no cover - discovery failures are rare
        raise GSCMonitorError(f"❌ Unable to construct Search Console client: {exc}") from exc


def fetch_search_analytics(
    service,
    *,
    site_url: str,
    start_date: dt.date,
    end_date: dt.date,
    dimensions: List[str] | None = None,
    row_limit: int = 10,
) -> Dict[str, Any]:
    body: Dict[str, Any] = {
        "startDate": start_date.isoformat(),
        "endDate": end_date.isoformat(),
        "rowLimit": row_limit,
    }
    if dimensions:
        body["dimensions"] = dimensions
    return service.searchanalytics().query(siteUrl=site_url, body=body).execute()


def fetch_sitemaps(service, *, site_url: str) -> Dict[str, Any]:
    return service.sitemaps().list(siteUrl=site_url).execute()


def inspect_url(service, *, site_url: str, inspection_url: str) -> Dict[str, Any]:
    body = {
        "inspectionUrl": inspection_url,
        "siteUrl": site_url,
    }
    return service.urlInspection().index().inspect(body=body).execute()


def summarize_search_performance(data: Dict[str, Any]) -> None:
    rows = data.get("rows") or []
    if not rows:
        print("⚠️  No search analytics data returned for the selected window.")
        return

    print("🔎 Top pages by clicks/impressions (last window):")
    for idx, row in enumerate(rows, start=1):
        keys = row.get("keys") or ["—"]
        page = keys[0]
        clicks = row.get("clicks", 0)
        impressions = row.get("impressions", 0)
        ctr = row.get("ctr", 0.0)
        position = row.get("position", 0.0)
        print(
            f"  {idx:2d}. {page}\n"
            f"       clicks={clicks:.0f}, impressions={impressions:.0f}, "
            f"ctr={ctr:.2%}, avg_position={position:.1f}"
        )

    thin_pages = [
        row
        for row in rows
        if row.get("impressions", 0) < 5 and row.get("clicks", 0) == 0
    ]
    if thin_pages:
        print("\n⚠️  Pages with low visibility (possible hreflang/canonical gaps):")
        for row in thin_pages[:5]:
            page = (row.get("keys") or ["—"])[0]
            print(f"   - {page} (0 clicks, {row.get('impressions', 0)} impressions)")


def summarize_sitemaps(data: Dict[str, Any]) -> None:
    sitemaps = data.get("sitemap", [])
    if not sitemaps:
        print("⚠️  No sitemaps registered in GSC; submit sitemap.xml in the Search Console UI.")
        return
    print("📬 Registered sitemaps:")
    for item in sitemaps:
        path = item.get("path")
        last_submitted = item.get("lastSubmitted")
        is_pending = item.get("isPending")
        warning = "⚠️  pending" if is_pending else ""
        print(f"  - {path} (last submitted {last_submitted}) {warning}")


def summarize_inspection(data: Dict[str, Any]) -> None:
    coverage = data.get("inspectionResult", {}).get("indexStatusResult", {})
    if not coverage:
        print("⚠️  No index inspection data returned.")
        return
    verdict = coverage.get("verdict", "UNKNOWN")
    coverage_state = coverage.get("coverageState", "UNKNOWN")
    robots = coverage.get("robotsTxtState", "UNKNOWN")
    print("🧭 Index inspection summary:")
    print(f"  - Verdict: {verdict}")
    print(f"  - Coverage: {coverage_state}")
    print(f"  - Robots state: {robots}")
    if issues := coverage.get("indexingStateExplanation"):
        print(f"  - Explanation: {issues}")


def _format_http_error(context: str, error: HttpError) -> str:
    status = getattr(getattr(error, "resp", None), "status", "unknown")
    reason = getattr(getattr(error, "resp", None), "reason", "unknown")
    if isinstance(error.content, bytes):
        detail = error.content.decode("utf-8", errors="ignore")
    else:
        detail = str(error.content)
    detail = detail.strip() or "no details"
    return f"❌ Failed to fetch {context} (status={status}, reason={reason}): {detail}"


def run_monitor(property_url: str, lookback_days: int, inspection_url: str | None = None) -> None:
    creds = _load_credentials()
    service = _build_service(creds)
    today = dt.date.today()
    start_date = today - dt.timedelta(days=lookback_days)

    inspector = inspection_url or DEFAULT_INSPECTION_URL
    print(f"🔐 Using Search Console service account: {getattr(creds, 'service_account_email', 'unknown')}")
    print(f"🌐 Property: {property_url}")
    print(f"🔍 Inspection URL: {inspector}")
    print(f"📅 Window: {start_date.isoformat()} → {today.isoformat()}")

    try:
        search_data = fetch_search_analytics(
            service,
            site_url=property_url,
            start_date=start_date,
            end_date=today,
            dimensions=["page"],
        )
    except HttpError as exc:
        raise GSCMonitorError(_format_http_error("search analytics", exc)) from exc
    summarize_search_performance(search_data)

    try:
        sitemap_data = fetch_sitemaps(service, site_url=property_url)
    except HttpError as exc:
        raise GSCMonitorError(_format_http_error("sitemaps", exc)) from exc
    summarize_sitemaps(sitemap_data)

    try:
        inspection_data = inspect_url(
            service,
            site_url=property_url,
            inspection_url=inspector,
        )
    except HttpError as exc:
        raise GSCMonitorError(_format_http_error("URL inspection", exc)) from exc
    summarize_inspection(inspection_data)

    print(
        "\n✅ GSC monitor finished. Use this output to confirm hreflang stability "
        "and highlight cannibalisation risks."
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Monitor Search Console metrics for lucy.world",
    )
    parser.add_argument(
        "--site",
        default=DEFAULT_PROPERTY,
        help="Search Console property identifier (default: sc-domain:lucy.world).",
    )
    parser.add_argument(
        "--lookback",
        type=int,
        default=7,
        help="Number of days to look back for analytics data (default: 7).",
    )
    parser.add_argument(
        "--inspection-url",
        default=DEFAULT_INSPECTION_URL,
        help="Full URL to inspect for coverage (default: https://lucy.world/).",
    )
    args = parser.parse_args()

    try:
        run_monitor(args.site, args.lookback, args.inspection_url)
    except GSCMonitorError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
