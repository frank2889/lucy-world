#!/usr/bin/env python3
"""Validate hreflang configuration against markets metadata.

Checks performed:
- Every market in markets/index.json has a matching markets/<CC>/hreflang.json file.
- market JSON country/defaultLocale/locales align between index and per-country file.
- Each locale entry defines code, hreflang, path, and canonical URL pointing to https://lucy.world/<lang>.
- Locale paths reference languages/<lang>/locale.json (source of truth for UI/meta strings).
- Alternate section includes the x-default entry pointing to the root.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANG_DIR = ROOT / "languages"
MARKETS_DIR = ROOT / "markets"


def _load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _normalize_lang(code: str) -> str:
    return code.split("-")[0].lower()


def validate_markets(index_path: Path) -> list[str]:
    issues: list[str] = []

    if not index_path.exists():
        return [f"Markets index not found: {index_path}"]

    try:
        index_data = _load_json(index_path)
    except Exception as exc:  # pragma: no cover - defensive
        return [f"Unable to parse markets index: {exc}"]

    markets = index_data.get("markets") if isinstance(index_data, dict) else None
    if not isinstance(markets, list):
        return ["markets/index.json must contain a 'markets' array"]

    # Build locale availability map
    available_langs = {p.name for p in LANG_DIR.iterdir() if p.is_dir() and len(p.name) == 2}

    for entry in markets:
        if not isinstance(entry, dict):
            issues.append("Invalid market entry (expected object)")
            continue

        code = entry.get("code")
        default_locale = entry.get("defaultLocale")
        canonical = entry.get("canonical")
        locales = entry.get("locales")

        if not isinstance(code, str) or len(code) != 2:
            issues.append(f"Invalid market code: {code!r}")
            continue

        folder = MARKETS_DIR / code.upper()
        hreflang_file = folder / "hreflang.json"
        if not hreflang_file.exists():
            issues.append(f"Missing markets/{code.upper()}/hreflang.json")
            continue

        try:
            hreflang_data = _load_json(hreflang_file)
        except Exception as exc:  # pragma: no cover - defensive
            issues.append(f"Invalid JSON in {hreflang_file}: {exc}")
            continue

        country = hreflang_data.get("country")
        if country != code.upper():
            issues.append(f"Country mismatch for {code}: expected {code.upper()}, found {country}")

        hl_default = hreflang_data.get("defaultLocale")
        if hl_default != default_locale:
            issues.append(
                f"Default locale mismatch for {code}: index={default_locale} / hreflang={hl_default}"
            )

        hl_locales = hreflang_data.get("locales")
        if not isinstance(hl_locales, list) or not hl_locales:
            issues.append(f"No locales defined in {hreflang_file}")
            continue

        # Collect locale codes from file
        locale_codes_in_file: set[str] = set()
        for loc in hl_locales:
            if not isinstance(loc, dict):
                issues.append(f"Invalid locale entry in {hreflang_file}")
                continue

            loc_code = loc.get("code")
            hreflang = loc.get("hreflang")
            path = loc.get("path")
            canon = loc.get("canonical")

            if not isinstance(loc_code, str):
                issues.append(f"Locale entry missing code in {hreflang_file}")
                continue

            primary = _normalize_lang(loc_code)
            locale_codes_in_file.add(primary)

            if primary not in available_langs:
                issues.append(f"Locale {primary} from {hreflang_file} missing languages/{primary}/locale.json")

            if not isinstance(hreflang, str) or not hreflang:
                issues.append(f"Locale {loc_code} missing hreflang in {hreflang_file}")

            if not isinstance(path, str) or not path.startswith("/"):
                issues.append(f"Locale {loc_code} has invalid path {path!r} in {hreflang_file}")
            elif path.rstrip("/") != f"/{primary}":
                issues.append(
                    f"Locale {loc_code} path mismatch: expected /{primary}, found {path} in {hreflang_file}"
                )

            expected_canonical = f"https://lucy.world/{primary}"
            if not isinstance(canon, str) or not canon.startswith("https://"):
                issues.append(f"Locale {loc_code} has invalid canonical {canon!r} in {hreflang_file}")
            elif canon.rstrip("/") != expected_canonical:
                issues.append(
                    f"Locale {loc_code} canonical mismatch: expected {expected_canonical}, found {canon}"
                )

        # Compare with index locale list
        index_locale_set = {(_normalize_lang(l) if isinstance(l, str) else "") for l in (locales or [])}
        index_locale_set.discard("")
        if index_locale_set != locale_codes_in_file:
            issues.append(
                f"Locale set mismatch for {code}: index={sorted(index_locale_set)} vs hreflang={sorted(locale_codes_in_file)}"
            )

        # Ensure x-default alternate present
        alternates = hreflang_data.get("alternate")
        if not isinstance(alternates, list) or not any(
            isinstance(alt, dict)
            and alt.get("hreflang") == "x-default"
            and alt.get("href") == "https://lucy.world/"
            for alt in alternates
        ):
            issues.append(f"Missing x-default alternate in {hreflang_file}")

        # Validate canonical from index matches default locale canonical
        if isinstance(canonical, str):
            expected_index_canonical = f"https://lucy.world/{_normalize_lang(default_locale)}"
            if canonical.rstrip("/") != expected_index_canonical:
                issues.append(
                    f"markets/index canonical mismatch for {code}: expected {expected_index_canonical}, found {canonical}"
                )
        else:
            issues.append(f"Market {code} missing canonical in index")

    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate hreflang reciprocity and market metadata")
    parser.add_argument("--markets", required=True, help="Path to markets/index.json")
    args = parser.parse_args(argv)

    index_path = (Path(args.markets)
                  if args.markets.startswith(('/', '.'))
                  else ROOT / args.markets)
    issues = validate_markets(index_path)

    if issues:
        for issue in issues:
            print(f"❌ {issue}")
        print(f"\nFound {len(issues)} hreflang issues.")
        return 1

    print("✅ Hreflang configuration verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
