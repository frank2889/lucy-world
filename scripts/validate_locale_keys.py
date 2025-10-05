#!/usr/bin/env python3
"""Audit locale string coverage against translator usage.

This script scans the frontend source code for calls to the translator helper
(`translate`, `translateOr`, or the `t` shorthand) and extracts every string key
that is requested at runtime. It then walks through every locale.json file under
the `languages/` directory and verifies that each locale exposes those keys.

Usage examples:

  python scripts/validate_locale_keys.py
      Prints a summary of missing keys per language (first 5 keys shown).

  python scripts/validate_locale_keys.py --limit 0 --strict
      Emits the full list of missing keys and exits with a non-zero status if
      any locale is incomplete.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

ROOT = Path(__file__).resolve().parents[1]
FRONTEND_SRC = ROOT / "frontend" / "src"
LANG_ROOT = ROOT / "languages"

def iter_source_files() -> Iterable[Path]:
    """Yield TypeScript/JavaScript source files within the frontend."""

    for path in FRONTEND_SRC.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".ts", ".tsx", ".js", ".jsx"}:
            yield path


def _extract_literal(remainder: str, quote: str) -> Optional[str]:
    """Extract the first string literal from remainder using the provided quote.

    Returns None on unterminated strings.
    """

    value: List[str] = []
    escaped = False
    for ch in remainder[1:]:
        if escaped:
            value.append(ch)
            escaped = False
            continue
        if ch == "\\":
            escaped = True
            continue
        if ch == quote:
            return "".join(value)
        value.append(ch)
    return None


def extract_translation_keys() -> Tuple[Set[str], Set[Tuple[Path, int]]]:
    """Return (keys, dynamic_usages).

    dynamic_usages captures call sites where the first argument is not a simple
    string literal, which the script cannot statically validate.
    """

    keys: Set[str] = set()
    dynamic_sites: Set[Tuple[Path, int]] = set()

    call_pattern = re.compile(r"\b(translateOr|translate|t)\s*\(", re.MULTILINE)

    for path in iter_source_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for match in call_pattern.finditer(text):
            start = match.end()
            remainder = text[start:]
            stripped = remainder.lstrip()
            if not stripped:
                continue

            leading_ws = len(remainder) - len(stripped)
            call_start_index = start + leading_ws
            line_number = text.count("\n", 0, call_start_index) + 1
            first_char = stripped[0]

            if first_char in {'"', '\''}:
                literal = _extract_literal(stripped, first_char)
                if literal is None:
                    dynamic_sites.add((path, line_number))
                else:
                    keys.add(literal)
            elif first_char == "`":
                dynamic_sites.add((path, line_number))
            else:
                dynamic_sites.add((path, line_number))

    return keys, dynamic_sites


def discover_languages() -> List[str]:
    languages: List[str] = []
    for entry in sorted(LANG_ROOT.iterdir()):
        if entry.is_dir() and len(entry.name) == 2 and entry.name.isalpha():
            if (entry / "locale.json").exists():
                languages.append(entry.name.lower())
    return languages


def load_locale_strings(lang: str) -> Tuple[Dict[str, str], Optional[str]]:
    path = LANG_ROOT / lang / "locale.json"
    if not path.exists():
        return {}, f"Missing locale.json for {lang}"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive
        return {}, f"Invalid JSON in {path}: {exc}"

    strings = data.get("strings")
    if not isinstance(strings, dict):
        return {}, f"Locale {lang} is missing 'strings' dictionary"
    return {str(key): str(value) for key, value in strings.items()}, None


def summarise_missing_keys(
    missing: Sequence[str],
    limit: int,
) -> str:
    if not missing:
        return ""
    if limit == 0 or len(missing) <= limit:
        preview = ", ".join(missing)
    else:
        preview = ", ".join(missing[:limit]) + f", … (+{len(missing) - limit} more)"
    return preview


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Validate locale key coverage")
    parser.add_argument(
        "--languages",
        nargs="*",
        help="Limit validation to the provided language codes",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of missing keys to display per locale (0 = unlimited)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if any locale is missing keys",
    )

    args = parser.parse_args(argv)

    used_keys, dynamic_sites = extract_translation_keys()

    print(f"🔎 Detected {len(used_keys)} translation keys in frontend source.")
    if dynamic_sites:
        print("⚠️  Skipping dynamic translator invocations (manual review recommended):")
        for path, line in sorted(dynamic_sites)[:10]:
            print(f"   - {path.relative_to(ROOT)}:{line}")
        if len(dynamic_sites) > 10:
            print(f"   … and {len(dynamic_sites) - 10} more")

    languages = args.languages or discover_languages()
    missing_total = 0
    problems: List[str] = []

    print("\nLocale coverage report:")
    for lang in languages:
        lang = lang.lower()
        strings, error = load_locale_strings(lang)
        if error:
            problems.append(error)
            missing_total += len(used_keys)
            print(f"- {lang}: ❌ {error}")
            continue

        missing = sorted(key for key in used_keys if key not in strings)
        if missing:
            missing_total += len(missing)
            preview = summarise_missing_keys(missing, args.limit)
            detail = f" (e.g. {preview})" if preview else ""
            print(f"- {lang}: ⚠️  missing {len(missing)} keys{detail}")
        else:
            print(f"- {lang}: ✅ all keys present")

    if problems:
        print("\nErrors:")
        for problem in problems:
            print(f"- {problem}")

    if missing_total == 0 and not problems:
        print("\n🎉 All locales contain the required keys.")
    else:
        print(f"\nSummary: {missing_total} missing keys across {len(languages)} locale(s).")

    if args.strict and (missing_total > 0 or problems):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
