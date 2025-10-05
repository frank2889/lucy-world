#!/usr/bin/env python3
"""Enforce enhanced locale metadata for all languages.

This script normalises `locale.json` meta fields and `structured.json`
outputs so they meet the architecture Definition of Done:

* meta.title/meta.description/meta.keywords must be populated
  and avoid the legacy placeholder strings.
* meta.description must have a length between 140 and 160 characters.
* structured.json must include an aiSemantic array with six values that
  align with the locale and mirror the updated meta data.

Run this script after updating languages or when localisation files are
imported from an external pipeline.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

ROOT = Path(__file__).resolve().parents[1]
LANGUAGE_DIR = ROOT / "languages"
REGISTRY_DIR = LANGUAGE_DIR / "registry"
BASE_URL = "https://lucy.world"


FALLBACK_TITLE = "Lucy World – Search intelligence for {name}"
FALLBACK_DESCRIPTION = (
    "Lucy World tracks live search demand and AI clustering for {name} audiences so teams plan "
    "weekly campaigns and sustainable growth with confidence."
)
FALLBACK_KEYWORDS = (
    "{name} keyword research",
    "{name} SEO insights",
    "search trends platform",
    "AI content planning",
    "{name} market analysis",
    "Lucy World intelligence",
)


PLACEHOLDER_TITLES: set[str] = {
    "Lucy World",
    "Lucy World – Global keyword research",
    "Lucy World – Clear insights for search and strategy",
}

PLACEHOLDER_DESCRIPTIONS: set[str] = {
    "Keyword research made simple with Google data: suggestions, trends, and insights.",
    "Discover keyword suggestions and search volume insights to plan smarter content.",
}

PLACEHOLDER_KEYWORDS: set[str] = {
    "keyword research, SEO, Google Trends, suggestions, search volume",
    "keyword research, SEO, Google Trends, suggestions, search volume, Lucy World",
}


@dataclass
class LocaleMeta:
    code: str
    name: str
    title: str
    description: str
    keywords: str
    ai_semantic: list[str]


def iter_language_dirs() -> Iterable[Path]:
    for entry in sorted(LANGUAGE_DIR.iterdir()):
        if entry.is_dir() and len(entry.name) == 2 and (entry / "locale.json").exists():
            yield entry


def load_language_name(code: str) -> str:
    registry_path = REGISTRY_DIR / f"{code}.json"
    if registry_path.exists():
        try:
            data = json.loads(registry_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
        name = data.get("name")
        if isinstance(name, str) and name.strip():
            return name.strip()
    return code.upper()


def ensure_meta_strings(code: str, strings: dict) -> LocaleMeta:
    lang_name = load_language_name(code)

    def _needs_replacement(value: str | None, placeholders: set[str]) -> bool:
        if not isinstance(value, str):
            return True
        candidate = value.strip()
        if not candidate:
            return True
        return candidate in placeholders

    title = strings.get("meta.title")
    if _needs_replacement(title, PLACEHOLDER_TITLES):
        title = FALLBACK_TITLE.format(name=lang_name)

    description = strings.get("meta.description")
    fallback_description = FALLBACK_DESCRIPTION.format(name=lang_name)
    if _needs_replacement(description, PLACEHOLDER_DESCRIPTIONS):
        description = fallback_description
    if not isinstance(description, str):
        description = fallback_description
    description = description.strip()
    if "This keeps marketing" in description:
        description = fallback_description
    if not 140 <= len(description) <= 160:
        description = fallback_description

    keywords = strings.get("meta.keywords")
    if isinstance(keywords, list):
        keywords = ", ".join(str(k) for k in keywords if str(k).strip())
    if not isinstance(keywords, str):
        keywords = str(keywords or "")
    if _needs_replacement(keywords, PLACEHOLDER_KEYWORDS):
        keywords = ", ".join(item.format(name=lang_name) for item in FALLBACK_KEYWORDS)

    keywords = keywords.strip()

    ai_semantic = [item.format(name=lang_name) for item in FALLBACK_KEYWORDS]

    strings["meta.title"] = title
    strings["meta.description"] = description
    strings["meta.keywords"] = keywords

    return LocaleMeta(
        code=code,
        name=lang_name,
        title=title,
        description=description,
        keywords=keywords,
        ai_semantic=ai_semantic,
    )


def render_structured(meta: LocaleMeta) -> str:
    home = f"{BASE_URL}/{meta.code}/"
    structured = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Organization",
                "name": "Lucy World",
                "url": f"{BASE_URL}/",
                "logo": f"{BASE_URL}/static/img/canva/logo-text.png",
            },
            {
                "@type": "WebSite",
                "name": meta.title,
                "url": home,
                "inLanguage": meta.code,
                "description": meta.description,
                "keywords": meta.keywords,
                "publisher": {"@type": "Organization", "name": "Lucy World"},
                "author": {"@type": "Organization", "name": "Lucy World"},
                "potentialAction": {
                    "@type": "SearchAction",
                    "target": f"{home}?q={{search_term_string}}",
                    "query-input": "required name=search_term_string",
                },
            },
            {
                "@type": "WebPage",
                "name": meta.title,
                "url": home,
                "inLanguage": meta.code,
                "isPartOf": {"@type": "WebSite", "url": home},
                "description": meta.description,
                "keywords": meta.keywords,
                "aiSemantic": meta.ai_semantic,
            },
        ],
    }

    return json.dumps(structured, ensure_ascii=False, indent=2) + "\n"


def process_language(lang_dir: Path, *, apply: bool) -> tuple[LocaleMeta, bool, bool]:
    locale_path = lang_dir / "locale.json"
    original_locale = locale_path.read_text(encoding="utf-8")
    data = json.loads(original_locale)

    strings = data.setdefault("strings", {})
    meta = ensure_meta_strings(lang_dir.name, strings)

    new_locale = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    locale_changed = new_locale != original_locale
    if apply and locale_changed:
        locale_path.write_text(new_locale, encoding="utf-8")

    structured_path = lang_dir / "structured.json"
    new_structured = render_structured(meta)
    try:
        original_structured = structured_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        original_structured = ""
    structured_changed = new_structured != original_structured
    if apply and structured_changed:
        structured_path.write_text(new_structured, encoding="utf-8")

    return meta, locale_changed, structured_changed


def resolve_languages(selected: Sequence[str] | None) -> list[Path]:
    selected_set = {code.lower() for code in selected or []}
    candidates = list(iter_language_dirs())
    if not selected_set:
        return candidates
    filtered: list[Path] = []
    for lang_dir in candidates:
        if lang_dir.name.lower() in selected_set:
            filtered.append(lang_dir)
    missing = selected_set - {path.name.lower() for path in filtered}
    if missing:
        raise SystemExit(f"Unknown language codes requested: {', '.join(sorted(missing))}")
    return filtered


def main() -> int:
    parser = argparse.ArgumentParser(description="Enhance locale metadata and structured data")
    parser.add_argument("--check", action="store_true", help="Fail if any locale requires updates")
    parser.add_argument("--langs", nargs="*", help="Limit processing to specific language codes")
    args = parser.parse_args()

    apply_changes = not args.check
    targets = resolve_languages(args.langs)
    total = len(targets)
    changed = 0

    for lang_dir in targets:
        meta, locale_changed, structured_changed = process_language(lang_dir, apply=apply_changes)
        if locale_changed or structured_changed:
            changed += 1
            action = "Updated" if apply_changes else "Would update"
            print(f"{action} {meta.code} ({meta.name})")

    if args.check:
        if changed > 0:
            print(f"{changed} of {total} locale(s) require enhancement. Run without --check to apply.")
            return 1
        print(f"All {total} locale(s) already conform to metadata requirements.")
    else:
        print(f"Processed {total} locale(s); updated {changed}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
