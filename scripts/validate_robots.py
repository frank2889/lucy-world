#!/usr/bin/env python3
"""Validate per-locale robots.txt files against crawl discipline DoD.

This script is intended for CI usage. It ensures that every locale robots file:
  * explicitly allows its own locale path and permitted hreflang alternates
  * keeps the blog section crawlable
  * disallows all unrelated language roots and deep paths
  * advertises the correct sitemap URL

Exit status is non-zero when any violations are detected.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from scripts.generate_site_assets import (  # type: ignore  # noqa: E402
    BASE_URL,
    SITES_DIR,
    _build_locale_relations,
    get_locales,
)


def _iter_lines(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _lang_codes_from_paths(paths: list[str]) -> set[str]:
    codes: set[str] = set()
    for path in paths:
        if "*" in path:
            continue
        if not path.startswith("/") or not path.endswith("/"):
            continue
        segment = path.strip("/").split("/")[0]
        if len(segment) == 2 and segment.isalpha():
            codes.add(segment.lower())
    return codes


def _collect_paths(lines: list[str], prefix: str) -> list[str]:
    result: list[str] = []
    for line in lines:
        if not line.lower().startswith(prefix):
            continue
        _, value = line.split(":", 1)
        result.append(value.strip())
    return result


def validate_locale(lang: str, all_locales: list[str], relations: dict[str, set[str]], path_map: dict[str, set[str]]) -> list[str]:
    issues: list[str] = []
    robots_path = SITES_DIR / lang / "robots.txt"
    sitemap_path = SITES_DIR / lang / "sitemap.xml"

    if not robots_path.is_file():
        issues.append(f"[{lang}] missing robots.txt")
        return issues
    if not sitemap_path.is_file():
        issues.append(f"[{lang}] missing sitemap.xml")

    lines = _iter_lines(robots_path)
    allow_paths = _collect_paths(lines, "allow:")
    disallow_paths = _collect_paths(lines, "disallow:")
    sitemap_lines = _collect_paths(lines, "sitemap:")

    # Blog must remain crawlable
    if "/blog/" not in allow_paths:
        issues.append(f"[{lang}] missing 'Allow: /blog/'")
    if "/blog/*" not in allow_paths:
        issues.append(f"[{lang}] missing 'Allow: /blog/*'")

    expected_codes = relations.get(lang, {lang})
    expected_paths = {p for code in expected_codes for p in path_map.get(code, {f"/{code}/"})}

    observed_allow_codes = _lang_codes_from_paths(allow_paths)
    if lang not in observed_allow_codes:
        issues.append(f"[{lang}] robots.txt must allow /{lang}/")

    missing_allowed = {code for code in expected_codes if code not in observed_allow_codes}
    if missing_allowed:
        issues.append(f"[{lang}] missing Allow directives for alternates: {sorted(missing_allowed)}")

    # Ensure all expected path variants are allowed
    def _normalized(path: str) -> str:
        value = path
        if value.endswith("*"):
            value = value[:-1]
        if not value.startswith("/"):
            value = f"/{value}"
        if not value.endswith("/"):
            value = f"{value}/"
        return value

    normalized_allow_paths = {_normalized(path) for path in allow_paths if "*" not in path}
    missing_paths = {path for path in expected_paths if path not in normalized_allow_paths}
    if missing_paths:
        issues.append(f"[{lang}] missing Allow paths: {sorted(missing_paths)}")

    if "/*/*/" not in disallow_paths:
        issues.append(f"[{lang}] missing 'Disallow: /*/*/'")
    if "/*?q=" not in disallow_paths:
        issues.append(f"[{lang}] missing 'Disallow: /*?q='")

    # All unrelated locales must be disallowed.
    unrelated = set(all_locales) - expected_codes
    disallowed_codes = _lang_codes_from_paths(disallow_paths)
    missing_disallows = sorted(code for code in unrelated if code not in disallowed_codes)
    if missing_disallows:
        issues.append(f"[{lang}] missing Disallow for locales: {missing_disallows}")

    expected_sitemap = f"{BASE_URL}/{lang}/sitemap.xml"
    if expected_sitemap not in sitemap_lines:
        issues.append(f"[{lang}] sitemap line should be '{expected_sitemap}'")

    return issues


def validate_all(locales: list[str]) -> list[str]:
    if not locales:
        return ["No locales discovered; ensure languages/ contains locale.json files"]

    relations, path_map = _build_locale_relations(locales)

    issues: list[str] = []
    for lang in locales:
        issues.extend(validate_locale(lang, locales, relations, path_map))
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate per-locale robots.txt files")
    parser.add_argument("--langs", nargs="*", help="Subset of languages to validate")
    args = parser.parse_args(argv)

    locales = args.langs if args.langs else get_locales()
    locales = [lang for lang in locales if (SITES_DIR / lang).is_dir()]

    issues = validate_all(locales)

    if issues:
        for issue in issues:
            print(f"❌ {issue}")
        print(f"\nFound {len(issues)} robots.txt issues across {len(locales)} locales.")
        return 1

    print(f"✅ Robots.txt validated for {len(locales)} locales.")
    return 0


if __name__ == "__main__":
    sys.exit(main())