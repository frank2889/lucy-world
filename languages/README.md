# Languages and dictionaries

This folder centralizes language configuration for Lucy World.

- `languages.json`: master list of languages we support (for URLs, hreflang, and sitemap). Use ISO 639-1 codes. We keep language-only paths (e.g., `en`, `nl`, `de`). This file seeds the per-language registry.
- `registry/`: one JSON per language (e.g., `en.json`, `nl.json`) containing `code`, `name`, `rtl`, `aliases`, and `hreflang`. The backend prefers this registry to derive supported languages and exposes `/meta/languages.json`.
- `dictionaries/`: per-language dictionaries, stopwords, stemming rules, or synonyms used by future features (e.g., advanced analysis, keyword normalization).
- `defaults.json`: (planned) locale defaults matrix that maps countries to initial language/market selections. Dutch visitors must default to `nl` + Netherlands without impacting other locales.

Update the list here to add/remove languages. The backend reads this file to generate:

- `/meta/sitemap.xml` entries per language.
- `<link rel="alternate" hreflang="...">` tags on pages.
- Locale-specific SEO assets (`languages/<lang>/robots.txt` and `sitemap.xml`) with the enforced `Disallow: /*?q=` crawl rule via `scripts/generate_site_assets.py`.

The frontend falls back to English if a translation file is missing.

## UX & CRO expectations (Oct 2025)

- Ensure localized strings exist for:
	- Sticky sidebar CTA (`Upgrade`, `Upgrade naar Premium`).
	- Credit purchase button (`Get AI credits`, `Koop AI-credits`).
	- Premium overlay copy (`Try Premium free for 7 days`).
- Update locale files whenever the CRO team introduces a new CTA or tooltip so the loader/error states stay consistent across 95+ languages.
- Add regression tests via `scripts/validate_locale_keys.py --strict` before each deploy.

## Generate per-language registry

Run the helper script to create or update one file per language under `languages/registry/`:

```bash
python3 scripts/generate_language_registry.py
```

Use `--force` to overwrite existing files.
