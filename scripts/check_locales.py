#!/usr/bin/env python3
import json
import os
import sys
from glob import glob

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCALES_DIR = os.path.join(BASE, 'languages', 'locales')

with open(os.path.join(LOCALES_DIR, 'en.json'), 'r', encoding='utf-8') as f:
    en = json.load(f)

en_keys = set(en.get('strings', {}).keys())

ok = True
for path in sorted(glob(os.path.join(LOCALES_DIR, '*.json'))):
    name = os.path.basename(path)
    if name == 'en.json' or name.lower() == 'readme.md':
        continue
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    keys = set(data.get('strings', {}).keys())
    missing = en_keys - keys
    extra = keys - en_keys
    if missing or extra:
        ok = False
        print(f"Locale {name}:", file=sys.stderr)
        if missing:
            print(f"  Missing keys: {sorted(missing)}", file=sys.stderr)
        if extra:
            print(f"  Extra keys: {sorted(extra)}", file=sys.stderr)

if ok:
    print('All locales match English keys (complete and consistent).')
    sys.exit(0)
else:
    sys.exit(1)
