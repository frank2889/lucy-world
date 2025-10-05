#!/usr/bin/env python3
"""Fill missing locale keys using the fallback language as source.

Usage:
    python scripts/backfill_locale_keys.py --locales af am ar

By default, uses English (en) strings as the fallback source and writes missing
keys into each target locale while keeping existing translations untouched.
The script formats JSON with sorted keys for deterministic diffs.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Iterable, Sequence

ROOT = Path(__file__).resolve().parents[1]
LANG_ROOT = ROOT / "languages"


def load_locale(lang: str) -> Dict[str, str]:
    path = LANG_ROOT / lang / "locale.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    strings = data.get("strings")
    if not isinstance(strings, dict):
        raise ValueError(f"Locale {lang} does not contain a 'strings' object")
    return {str(k): str(v) for k, v in strings.items()}


def save_locale(lang: str, strings: Dict[str, str]) -> None:
    path = LANG_ROOT / lang / "locale.json"
    payload = {
        "lang": lang,
        "dir": "ltr",
        "strings": dict(sorted(strings.items())),
    }
    # Preserve original dir when possible
    original = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(original.get("dir"), str):
        payload["dir"] = original["dir"]
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def backfill(locales: Sequence[str], source_lang: str = "en") -> Iterable[str]:
    source_strings = load_locale(source_lang)
    updated_locales = []
    for locale in locales:
        locale = locale.lower()
        strings = load_locale(locale)
        missing = {k: v for k, v in source_strings.items() if k not in strings}
        if not missing:
            continue
        strings.update(missing)
        save_locale(locale, strings)
        updated_locales.append((locale, len(missing)))
    return [f"{loc} (+{count})" for loc, count in updated_locales]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Backfill missing locale keys")
    parser.add_argument("--locales", nargs="+", help="Locales to update (e.g. af am ar)")
    parser.add_argument("--source", default="en", help="Source locale to copy strings from")
    args = parser.parse_args(argv)

    changed = backfill(args.locales, source_lang=args.source)
    if changed:
        print("Updated locales:", ", ".join(changed))
    else:
        print("No locales required backfill")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())