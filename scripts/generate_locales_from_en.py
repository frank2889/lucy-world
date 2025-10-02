#!/usr/bin/env python3
"""
Generate one Shopify-style locale JSON per supported language under /locales using English keys.
If a file exists, it is left untouched unless --force is passed. RTL is set for ar, he, fa, ur.
"""
import json
import os
import argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG_DIR = os.path.join(ROOT, 'languages', 'registry')
LANG_DIR = os.path.join(ROOT, 'languages')
LEGACY_LOCALES_DIR = os.path.join(ROOT, 'languages', 'locales')
VERY_LEGACY_DIR = os.path.join(ROOT, 'locales')
EN_PATH = None
for candidate in (
    os.path.join(LANG_DIR, 'en', 'locale.json'),
    os.path.join(LEGACY_LOCALES_DIR, 'en.json'),
    os.path.join(LEGACY_LOCALES_DIR, 'en.default.json'),
    os.path.join(VERY_LEGACY_DIR, 'en.json'),
    os.path.join(VERY_LEGACY_DIR, 'en.default.json'),
):
    if candidate and os.path.exists(candidate):
        EN_PATH = candidate
        break
RTL = {'ar','he','fa','ur'}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--codes', type=str, help='Comma-separated ISO 639-1 codes to generate (e.g., "es,fr,de")')
    ap.add_argument('--i-understand-this-will-overwrite-translations', action='store_true', 
                    help='Required flag to acknowledge this will overwrite existing translations')
    args = ap.parse_args()

    if not args.i_understand_this_will_overwrite_translations:
        print("⚠️  WARNING: This script will OVERWRITE existing translations!")
        print("   All localized content in languages/*/locale.json will be replaced with English text.")
        print("   This will destroy translation work. Only use for NEW language setup.")
        print("   Add --i-understand-this-will-overwrite-translations to proceed.")
        return 1

    if not EN_PATH or not os.path.exists(EN_PATH):
        raise SystemExit('Missing English locale file (languages/en/locale.json or legacy locales).')

    with open(EN_PATH, 'r', encoding='utf-8') as f:
        en = json.load(f)
        en_strings = en.get('strings', {})

    os.makedirs(LANG_DIR, exist_ok=True)

    if args.codes:
        codes = [c.strip().lower() for c in args.codes.split(',') if c.strip()]
    else:
        codes = []
        if os.path.isdir(REG_DIR):
            for name in sorted(os.listdir(REG_DIR)):
                if name.endswith('.json'):
                    codes.append(name[:-5])
        else:
            codes = ['en','nl']

    for code in codes:
        # skip English default (already exists)
        if code == 'en':
            continue
        out_dir = os.path.join(LANG_DIR, code)
        os.makedirs(out_dir, exist_ok=True)
        out = os.path.join(out_dir, 'locale.json')
        if os.path.exists(out) and not args.force:
            continue
        data = {
            'lang': code,
            'dir': 'rtl' if code in RTL else 'ltr',
            'strings': en_strings,
        }
        with open(out, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Locales generated/updated under {LANG_DIR}")

if __name__ == '__main__':
    main()
