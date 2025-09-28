#!/usr/bin/env python3
"""
Generate per-locale site assets (robots.txt, sitemap.xml, structured.json)
under languages/<lang>/ for all available locales from languages/locales/.
If an asset already exists, it will be left untouched unless --force is used.
"""
import argparse
import datetime as dt
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCALES_DIR = ROOT / 'languages' / 'locales'
SITES_DIR = ROOT / 'languages'
BASE_URL = os.environ.get('BASE_URL', 'https://lucy.world')
TODAY = dt.date.today().isoformat()

DEFAULT_ROBOTS = """User-agent: *
Allow: /

Sitemap: {base}/{lang}/sitemap.xml
""".strip()

DEFAULT_SITEMAP = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{base}/{lang}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
""".strip()

DEFAULT_STRUCTURED = {
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
            "name": "Lucy World",
            "url": None,  # filled per-lang
            "inLanguage": None,  # filled per-lang
            "description": "Keyword research made simple with Google data: suggestions, trends, and insights.",
            "keywords": "keyword research, SEO, Google Trends, suggestions, search volume",
            "publisher": {"@type": "Organization", "name": "Lucy World"},
            "author": {"@type": "Organization", "name": "Lucy World"},
            "potentialAction": {
                "@type": "SearchAction",
                "target": None,  # filled per-lang
                "query-input": "required name=search_term_string",
            },
        },
        {
            "@type": "WebPage",
            "name": "Lucy World",
            "url": None,  # filled per-lang
            "inLanguage": None,  # filled per-lang
            "isPartOf": {"@type": "WebSite", "url": None},  # filled per-lang
            "description": "Keyword research made simple with Google data: suggestions, trends, and insights.",
            "keywords": "keyword research, SEO, Google Trends, suggestions, search volume"
        },
    ],
}


def get_locales():
    if not LOCALES_DIR.is_dir():
        return []
    return sorted(p.stem for p in LOCALES_DIR.glob('*.json'))


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def write_if_missing(path: Path, content: str, force: bool):
    if path.exists() and not force:
        return False
    path.write_text(content, encoding='utf-8')
    return True


def generate_for_lang(lang: str, force: bool = False):
    out_dir = (SITES_DIR / lang)
    ensure_dir(out_dir)

    robots = DEFAULT_ROBOTS.format(base=BASE_URL, lang=lang)
    sitemap = DEFAULT_SITEMAP.format(base=BASE_URL, lang=lang, today=TODAY)

    structured = DEFAULT_STRUCTURED.copy()
    # Deep copy and fill fields
    import copy

    structured = copy.deepcopy(DEFAULT_STRUCTURED)
    home = f"{BASE_URL}/{lang}/"
    structured["@graph"][1]["url"] = home
    structured["@graph"][1]["inLanguage"] = lang
    structured["@graph"][1]["potentialAction"]["target"] = home + "?q={search_term_string}"
    structured["@graph"][2]["url"] = home
    structured["@graph"][2]["inLanguage"] = lang
    structured["@graph"][2]["isPartOf"]["url"] = home

    # Merge meta from locales/<lang>.json if available
    def load_locale_meta(l: str):
        fp = LOCALES_DIR / f"{l}.json"
        if not fp.exists():
            return None
        try:
            data = json.loads(fp.read_text(encoding='utf-8'))
            strings = data.get('strings') if isinstance(data, dict) else None
            if not isinstance(strings, dict):
                return None
            title = strings.get('meta.title') or strings.get('meta_title')
            desc = strings.get('meta.description') or strings.get('meta_description')
            kw = strings.get('meta.keywords') or strings.get('meta_keywords')
            # Normalize keywords to comma-separated string
            if isinstance(kw, list):
                kw = ", ".join(str(x) for x in kw)
            elif kw is not None:
                kw = str(kw)
            return {
                'title': title,
                'description': desc,
                'keywords': kw,
            }
        except Exception:
            return None

    meta = load_locale_meta(lang) or {}
    for idx in (1, 2):  # WebSite and WebPage nodes
        node = structured["@graph"][idx]
        if meta.get('title'):
            node['name'] = meta['title']
        if meta.get('description'):
            node['description'] = meta['description']
        if meta.get('keywords'):
            node['keywords'] = meta['keywords']

    changed = False
    changed |= write_if_missing(out_dir / 'robots.txt', robots + "\n", force)
    changed |= write_if_missing(out_dir / 'sitemap.xml', sitemap + "\n", force)
    changed |= write_if_missing(out_dir / 'structured.json', json.dumps(structured, ensure_ascii=False, indent=2) + "\n", force)
    return changed


def main():
    parser = argparse.ArgumentParser(description='Generate per-locale site assets')
    parser.add_argument('--force', action='store_true', help='Overwrite existing files')
    parser.add_argument('--langs', nargs='*', help='Limit to specific languages (e.g., en nl de)')
    parser.add_argument('--exclude', nargs='*', default=[], help='Exclude languages (e.g., en nl)')
    # No legacy layout; always write to languages/<lang>/*
    args = parser.parse_args()

    ensure_dir(SITES_DIR)

    locales = args.langs if args.langs else get_locales()
    if args.exclude:
        excludes = set(args.exclude)
        locales = [l for l in locales if l not in excludes]
    if not locales:
        print('No locales found in languages/locales; nothing to do.')
        return 0

    total_changed = 0
    for lang in locales:
        if len(lang) != 2 or not lang.isalpha():
            continue
        changed = generate_for_lang(lang, force=args.force)
        if changed:
            total_changed += 1
            print(f"Generated/updated assets for {lang}")

    print(f"Done. Languages processed: {len(locales)}; changes: {total_changed}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
