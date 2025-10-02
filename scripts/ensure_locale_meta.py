#!/usr/bin/env python3
"""
Ensure every locale JSON includes meta keys.

Supports the new layout (languages/<lang>/locale.json) with fallback to
legacy directories (languages/locales/*.json, locales/*.json).
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANG_DIR = ROOT / 'languages'
LEGACY_LOCALES_DIR = ROOT / 'languages' / 'locales'
VERY_LEGACY_DIR = ROOT / 'locales'

DEFAULTS = {
    'meta.title': 'Lucy World',
    'meta.description': 'Keyword research made simple with Google data: suggestions, trends, and insights.',
    'meta.keywords': 'keyword research, SEO, Google Trends, suggestions, search volume',
}

# Only use defaults if meta fields are completely missing, not if they have localized content
def should_use_default(current_value, default_value):
    """Only use default if field is missing, empty, or exactly matches the old default"""
    if current_value is None or current_value == '':
        return True
    # Don't overwrite if it's already localized (different from default)
    if current_value != default_value:
        return False
    return True


def load_json(p: Path):
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception:
        return None


def save_json(p: Path, data):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding='utf-8')


def ensure_meta(p: Path) -> bool:
    data = load_json(p)
    if not isinstance(data, dict):
        return False
    strings = data.get('strings')
    if not isinstance(strings, dict):
        return False
    changed = False
    for k, v in DEFAULTS.items():
        current = strings.get(k)
        if should_use_default(current, v):
            strings[k] = v
            changed = True
    if changed:
        data['strings'] = strings
        save_json(p, data)
    return changed


def iter_locale_files():
    found = False
    if LANG_DIR.is_dir():
        for entry in sorted(LANG_DIR.iterdir()):
            if not entry.is_dir():
                continue
            fp = entry / 'locale.json'
            if fp.exists():
                found = True
                yield fp
    if LEGACY_LOCALES_DIR.is_dir():
        for fp in sorted(LEGACY_LOCALES_DIR.glob('*.json')):
            found = True
            yield fp
    if VERY_LEGACY_DIR.is_dir():
        for fp in sorted(VERY_LEGACY_DIR.glob('*.json')):
            found = True
            yield fp
    if not found:
        print('No locale files found.')


def main() -> int:
    total = 0
    changed = 0
    for fp in iter_locale_files() or []:
        total += 1
        if ensure_meta(fp):
            changed += 1
            print(f"Updated meta keys: {fp}")
    print(f"Done. Locales processed: {total}; files updated: {changed}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
