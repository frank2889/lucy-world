#!/usr/bin/env python3
"""Verify the Growth Flywheel loop end-to-end.

This script checks that:
  * candidate queries exist and have recent activity
  * at least one candidate reached the published state during the past 30 days
  * every published candidate has a published draft with persisted files
  * published drafts appear in the blog feed manifest and locale sitemaps

Exit code 0 = flywheel healthy, non-zero indicates which checks failed.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend import create_app  # type: ignore  # noqa: E402
from backend.models import CandidateQuery, ContentDraft  # type: ignore  # noqa: E402
from scripts.generate_site_assets import get_locales  # type: ignore  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BLOG_FEED = ROOT / "content" / "published" / "feed.json"
LANG_DIR = ROOT / "languages"


def _load_manifest() -> dict[str, dict[str, str]]:
    if not BLOG_FEED.is_file():
        return {}
    try:
        payload = json.loads(BLOG_FEED.read_text(encoding="utf-8"))
    except Exception:
        return {}
    posts = payload.get("posts") if isinstance(payload, dict) else None
    if not isinstance(posts, list):
        return {}
    manifest: dict[str, dict[str, str]] = {}
    for post in posts:
        if not isinstance(post, dict):
            continue
        slug = str(post.get("slug") or "").strip()
        if slug:
            manifest[slug] = post
    return manifest


def _sitemap_contains(lang: str, slug: str) -> bool:
    sitemap = LANG_DIR / lang / "sitemap.xml"
    if not sitemap.is_file():
        return False
    pattern = re.compile(rf"/blog/{re.escape(slug)}/?")
    try:
        return bool(pattern.search(sitemap.read_text(encoding="utf-8")))
    except Exception:
        return False


def _as_utc(dt_value: datetime) -> datetime:
    if dt_value.tzinfo is None:
        return dt_value.replace(tzinfo=timezone.utc)
    return dt_value.astimezone(timezone.utc)


def verify_recent_published(published_drafts: list[ContentDraft], window_days: int) -> tuple[bool, list[str]]:
    window = datetime.now(timezone.utc) - timedelta(days=window_days)
    recent = [
        draft for draft in published_drafts
        if draft.published_at and _as_utc(draft.published_at) >= window
    ]
    if recent:
        return True, [f"Found {len(recent)} published drafts within the last {window_days} days."]
    latest = max((draft.published_at for draft in published_drafts if draft.published_at), default=None)
    latest_str = _as_utc(latest).isoformat() if latest else "none"
    return False, [
        "No published drafts found in the recent window",
        f"Most recent publish date: {latest_str}"
    ]


def verify_flywheel(window_days: int = 30) -> tuple[bool, list[str]]:
    issues: list[str] = []
    manifest = _load_manifest()
    locales = get_locales()

    total_candidates = CandidateQuery.query.count()
    if total_candidates == 0:
        issues.append("No candidate queries recorded.")

    status_counts = Counter(
        status for status, in CandidateQuery.query.with_entities(CandidateQuery.status).all()
    )

    published_candidates: list[CandidateQuery] = (
        CandidateQuery.query.filter(CandidateQuery.status == "published").all()
    )

    if not published_candidates:
        issues.append("No candidates have reached the published state.")

    published_drafts: list[ContentDraft] = (
        ContentDraft.query.filter(ContentDraft.status == "published").all()
    )

    if not published_drafts:
        issues.append("No published drafts exist.")
    else:
        ok_recent, msg_recent = verify_recent_published(published_drafts, window_days)
        if not ok_recent:
            issues.extend(msg_recent)

    # Cross-validate each published candidate/draft pair
    for candidate in published_candidates:
        drafts = [draft for draft in published_drafts if draft.candidate_id == candidate.id]
        if not drafts:
            issues.append(f"Candidate {candidate.id} ({candidate.keyword}) lacks a published draft.")
            continue
        for draft in drafts:
            slug = draft.slug
            if slug not in manifest:
                issues.append(f"Published draft {slug} not present in blog feed manifest.")
            lang = (draft.language or "en").split("-")[0].lower()
            if lang not in locales:
                issues.append(f"Draft {slug} references unknown locale '{lang}'.")
            elif not _sitemap_contains(lang, slug):
                issues.append(f"Locale sitemap for {lang} missing blog entry {slug}.")
            markdown_path = ROOT / "content" / "published" / f"{slug}.md"
            html_path = ROOT / "static" / "blog" / f"{slug}.html"
            if not markdown_path.is_file() or not html_path.is_file():
                issues.append(f"Published draft {slug} missing exported files.")

    summary_lines = [
        f"Total candidates: {total_candidates}",
        f"Status counts: {dict(status_counts)}",
        f"Published candidates: {len(published_candidates)}",
        f"Published drafts: {len(published_drafts)}",
        f"Manifest entries: {len(manifest)}",
    ]

    return len(issues) == 0, summary_lines + issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify Growth Flywheel health")
    parser.add_argument("--window", type=int, default=30, help="Days to consider for recent publish activity")
    args = parser.parse_args(argv)

    app = create_app()
    with app.app_context():
        ok, messages = verify_flywheel(window_days=args.window)

    for line in messages:
        print(line)

    if ok:
        print("✅ Growth flywheel verified.")
        return 0
    print("❌ Growth flywheel check failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())