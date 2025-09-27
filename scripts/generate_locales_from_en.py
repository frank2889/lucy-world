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
LOCALES_DIR = os.path.join(ROOT, 'locales')
EN_PATH = os.path.join(LOCALES_DIR, 'en.default.json')
RTL = {'ar','he','fa','ur'}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--codes', type=str, help='Comma-separated ISO 639-1 codes to generate (e.g., "es,fr,de")')
    args = ap.parse_args()

    if not os.path.exists(EN_PATH):
        raise SystemExit('Missing locales/en.default.json as the source of keys')

    with open(EN_PATH, 'r', encoding='utf-8') as f:
        en = json.load(f)
        en_strings = en.get('strings', {})

    os.makedirs(LOCALES_DIR, exist_ok=True)

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
        out = os.path.join(LOCALES_DIR, f'{code}.json')
        if os.path.exists(out) and not args.force:
            continue
        data = {
            'lang': code,
            'dir': 'rtl' if code in RTL else 'ltr',
            'strings': en_strings,
        }
        with open(out, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Locales generated/updated in {LOCALES_DIR}")

if __name__ == '__main__':
    main()
