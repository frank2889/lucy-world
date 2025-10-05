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
from typing import Any, Optional, Set

ROOT = Path(__file__).resolve().parents[1]
SITES_DIR = ROOT / 'languages'
MARKETS_DIR = ROOT / 'markets'
BASE_URL = os.environ.get('BASE_URL', 'https://lucy.world')
TODAY = dt.date.today().isoformat()
BLOG_FEED_PATH = ROOT / 'content' / 'published' / 'feed.json'

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


def _load_blog_posts() -> list[dict[str, Any]]:
    if not BLOG_FEED_PATH.is_file():
        return []
    try:
        payload = json.loads(BLOG_FEED_PATH.read_text(encoding='utf-8'))
    except Exception:
        return []
    posts = payload.get('posts') if isinstance(payload, dict) else None
    if not isinstance(posts, list):
        return []
    return [post for post in posts if isinstance(post, dict)]


def _format_lastmod(value: str | None) -> str | None:
    if not value:
        return None
    try:
        dt_value = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
        return dt_value.date().isoformat()
    except Exception:
        return None


def _render_urlset(entries: list[dict[str, str]]) -> str:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for entry in entries:
        lines.append('  <url>')
        lines.append(f"    <loc>{entry['loc']}</loc>")
        lastmod = entry.get('lastmod')
        if lastmod:
            lines.append(f"    <lastmod>{lastmod}</lastmod>")
        changefreq = entry.get('changefreq')
        if changefreq:
            lines.append(f"    <changefreq>{changefreq}</changefreq>")
        priority = entry.get('priority')
        if priority:
            lines.append(f"    <priority>{priority}</priority>")
        lines.append('  </url>')
    lines.append('</urlset>')
    return "\n".join(lines)


def locale_json_path(lang: str) -> Optional[Path]:
    candidate = SITES_DIR / lang / 'locale.json'
    if candidate.exists():
        return candidate
    legacy = ROOT / 'languages' / 'locales' / f'{lang}.json'
    if legacy.exists():
        return legacy
    very_legacy = ROOT / 'locales' / f'{lang}.json'
    if very_legacy.exists():
        return very_legacy
    return None


def get_locales() -> list[str]:
    locales: Set[str] = set()
    if SITES_DIR.is_dir():
        for entry in SITES_DIR.iterdir():
            if entry.is_dir() and (entry / 'locale.json').exists():
                locales.add(entry.name)
    # legacy fallback
    legacy_dir = ROOT / 'languages' / 'locales'
    if legacy_dir.is_dir():
        for fp in legacy_dir.glob('*.json'):
            locales.add(fp.stem)
    return sorted(locales)


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def write_if_missing(path: Path, content: str, force: bool):
    if path.exists():
        existing = path.read_text(encoding='utf-8')
        if not force and existing == content:
            return False
        if not force and existing != content:
            path.write_text(content, encoding='utf-8')
            return True
        if force:
            path.write_text(content, encoding='utf-8')
            return True
        return False
    path.write_text(content, encoding='utf-8')
    return True

def _normalize_path(candidate: str | None, code: str) -> str:
    candidate = (candidate or '').strip() or f'/{code}'
    if not candidate.startswith('/'):
        candidate = f'/{candidate}'
    if not candidate.endswith('/'):
        candidate = f'{candidate}/'
    return candidate


def _build_locale_relations(all_locales: list[str]):
    from collections import defaultdict

    groups: dict[str, set[str]] = defaultdict(set)
    paths: dict[str, set[str]] = defaultdict(set)

    if MARKETS_DIR.is_dir():
        for entry in MARKETS_DIR.iterdir():
            hreflang_path = entry / 'hreflang.json'
            if not hreflang_path.is_file():
                continue
            try:
                data = json.loads(hreflang_path.read_text(encoding='utf-8'))
            except Exception:
                continue
            locales = data.get('locales') if isinstance(data, dict) else None
            if not isinstance(locales, list):
                continue
            codes: list[str] = []
            for loc in locales:
                if not isinstance(loc, dict):
                    continue
                code = loc.get('code')
                if not isinstance(code, str):
                    continue
                primary = code.split('-')[0].lower()
                if len(primary) != 2 or not primary.isalpha():
                    continue
                norm_path = _normalize_path(loc.get('path'), primary)
                paths[primary].add(norm_path)
                codes.append(primary)
            for code in codes:
                groups[code].update(codes)

    for lang in all_locales:
        groups.setdefault(lang, set()).add(lang)
        if lang not in paths:
            paths[lang].add(f'/{lang}/')
        else:
            paths[lang] = {_normalize_path(p, lang) for p in paths[lang]}

    return groups, paths


def _build_robots(lang: str, all_locales: list[str], relations: dict[str, set[str]], path_map: dict[str, set[str]]):
    allowed_codes = relations.get(lang, {lang})
    lines = ["User-agent: *"]
    lines.append("Allow: /blog/")
    lines.append("Allow: /blog/*")

    seen_paths: set[str] = set()

    def _append_paths(code: str):
        for path in sorted(path_map.get(code, {f'/{code}/'})):
            norm = _normalize_path(path, code)
            if norm not in seen_paths:
                lines.append(f"Allow: {norm}")
                seen_paths.add(norm)

    _append_paths(lang)
    for code in sorted(allowed_codes - {lang}):
        _append_paths(code)

    disallowed = sorted(set(all_locales) - set(allowed_codes))
    for code in disallowed:
        lines.append(f"Disallow: /{code}/")

    lines.append("Disallow: /*/*/")
    lines.append("")
    lines.append(f"Sitemap: {BASE_URL}/{lang}/sitemap.xml")
    return "\n".join(lines) + "\n"


def generate_for_lang(lang: str, *, force: bool = False, all_locales: list[str], relations: dict[str, set[str]], path_map: dict[str, set[str]], blog_posts: list[dict[str, Any]]):
    out_dir = (SITES_DIR / lang)
    ensure_dir(out_dir)

    url_entries: list[dict[str, str]] = [{
        'loc': f"{BASE_URL}/{lang}/",
        'lastmod': TODAY,
        'changefreq': 'daily',
        'priority': '1.0',
    }]

    for post in blog_posts:
        post_lang = str(post.get('language') or 'en').split('-')[0].lower()
        if post_lang != lang:
            continue
        url = post.get('url') if isinstance(post.get('url'), str) else None
        if not url:
            slug = post.get('slug') if isinstance(post.get('slug'), str) else None
            if not slug:
                continue
            slug = slug.strip('/')
            url = f"{BASE_URL}/blog/{slug}/"
        lastmod = _format_lastmod(post.get('published_at')) or TODAY
        url_entries.append({
            'loc': url,
            'lastmod': lastmod,
            'changefreq': 'weekly',
            'priority': '0.6',
        })

    sitemap = _render_urlset(url_entries)

    # Check if structured.json already exists and has enhanced content
    structured_path = out_dir / 'structured.json'
    has_enhanced_structured = False
    
    if structured_path.exists():
        try:
            existing_structured = json.loads(structured_path.read_text(encoding='utf-8'))
            # Check if it has our enhanced aiSemantic field or localized descriptions
            if isinstance(existing_structured, dict):
                graph = existing_structured.get('@graph', [])
                for node in graph:
                    if isinstance(node, dict):
                        # Check for aiSemantic field (our enhancement)
                        if 'aiSemantic' in node:
                            has_enhanced_structured = True
                            break
                        # Check for non-default descriptions (localized content)
                        desc = node.get('description', '')
                        if desc and desc != "Keyword research made simple with Google data: suggestions, trends, and insights.":
                            has_enhanced_structured = True
                            break
        except Exception:
            pass
    
    # Only generate structured.json if it doesn't exist or doesn't have enhanced content
    # (unless force is used)
    skip_structured = has_enhanced_structured and not force

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
        fp = locale_json_path(l)
        if not fp:
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

    robots_content = _build_robots(lang, all_locales, relations, path_map)

    changed = False
    changed |= write_if_missing(out_dir / 'robots.txt', robots_content, force)
    changed |= write_if_missing(out_dir / 'sitemap.xml', sitemap + "\n", force)
    
    # Only write structured.json if it doesn't have enhanced content or force is used
    if not skip_structured:
        changed |= write_if_missing(out_dir / 'structured.json', json.dumps(structured, ensure_ascii=False, indent=2) + "\n", force)
    elif has_enhanced_structured and not force:
        # Print info about preserving enhanced content
        print(f"  Preserving enhanced structured.json for {lang} (use --force to overwrite)")
    
    return changed


def main():
    parser = argparse.ArgumentParser(description='Generate per-locale site assets')
    parser.add_argument('--all', action='store_true', help='Process all locales (default behavior)')
    parser.add_argument('--force', action='store_true', help='Overwrite existing files')
    parser.add_argument('--langs', nargs='*', help='Limit to specific languages (e.g., en nl de)')
    parser.add_argument('--exclude', nargs='*', default=[], help='Exclude languages (e.g., en nl)')
    # No legacy layout; always write to languages/<lang>/*
    args = parser.parse_args()

    ensure_dir(SITES_DIR)

    all_locales = get_locales()
    locales = args.langs if args.langs else list(all_locales)
    if args.exclude:
        excludes = set(args.exclude)
        locales = [l for l in locales if l not in excludes]
    if not locales:
        print('No locales found in languages/locales; nothing to do.')
        return 0

    relations, path_map = _build_locale_relations(all_locales)
    blog_posts = _load_blog_posts()

    total_changed = 0
    for lang in locales:
        if len(lang) != 2 or not lang.isalpha():
            continue
        changed = generate_for_lang(
            lang,
            force=args.force,
            all_locales=all_locales,
            relations=relations,
            path_map=path_map,
            blog_posts=blog_posts,
        )
        if changed:
            total_changed += 1
            print(f"Generated/updated assets for {lang}")

    print(f"Done. Languages processed: {len(locales)}; changes: {total_changed}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
