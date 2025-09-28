#!/usr/bin/env python3
"""
Ensure all languages/locales/<lang>.json contain meta keys in strings:
- meta.title
- meta.description
- meta.keywords
Defaults are English; translate later per locale. Existing values are preserved.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCALES_DIR = ROOT / 'languages' / 'locales'

DEFAULTS = {
    'meta.title': 'Lucy World',
    'meta.description': 'Keyword research made simple with Google data: suggestions, trends, and insights.',
    'meta.keywords': 'keyword research, SEO, Google Trends, suggestions, search volume',
}

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
        if k not in strings or strings[k] in (None, ''):
            strings[k] = v
            changed = True
    if changed:
        data['strings'] = strings
        save_json(p, data)
    return changed


def main() -> int:
    if not LOCALES_DIR.is_dir():
        print('No locales dir; nothing to do.')
        return 0
    total = 0
    changed = 0
    for fp in sorted(LOCALES_DIR.glob('*.json')):
        total += 1
        if ensure_meta(fp):
            changed += 1
            print(f"Updated meta keys: {fp.name}")
    print(f"Done. Locales processed: {total}; files updated: {changed}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
