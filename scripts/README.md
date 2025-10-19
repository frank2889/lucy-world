# Scripts Documentation

This directory contains maintenance and validation scripts for the Lucy
World localization system.

## Scripts Overview

### ✅ `ensure_locale_meta.py`

**Status:** Updated to preserve translations

- Ensures locale files have required meta fields
- **Now preserves existing localized content** — only adds defaults for
  missing fields
- Safe to run on translated content
- Usage:
  `python3 scripts/ensure_locale_meta.py`

### ✅ `generate_language_registry.py`

**Status:** Up to date and safe

- Generates registry files under `languages/registry/` with language
  metadata
- Only creates missing files unless `--force` is used
- Usage:
  `python3 scripts/generate_language_registry.py [--force]`

### ⚠️ `generate_locales_from_en.py`

**Status:** Updated with safety warnings

- **DANGER**: This script overwrites all translations with English text
- Now requires `--i-understand-this-will-overwrite-translations` flag
- Only use for setting up NEW languages, never on existing translations
- Usage:
  `python3 scripts/generate_locales_from_en.py --codes "xx,yy" --i-understand-this-will-overwrite-translations`

### ✅ `generate_site_assets.py`

**Status:** Updated to preserve enhanced content

- Generates robots.txt, sitemap.xml, and structured.json files,
  including the global `Disallow: /*?q=` rule for SERP URLs
- **Now detects and preserves enhanced structured.json files** with:
  - Localized descriptions (non-default content)
  - aiSemantic arrays
  - Market-specific keywords
- Use `--force` to overwrite enhanced content (not recommended)
- Usage:
  `python3 scripts/generate_site_assets.py [--langs xx yy zz] [--force]`

### ✅ `migrate_add_user_plan_columns.py`

**Status:** New migration helper (Oct 2025)

- Adds the `plan`, `plan_started_at`, `plan_metadata`, Stripe, and
  billing columns to the production `users` table if they are missing
- Recreates the indexes expected by SQLAlchemy (`plan`,
  `billing_country`, Stripe unique keys)
- Safe to run repeatedly; creates a timestamped `.bak` backup before
  applying changes
- Usage:
  `python3 scripts/migrate_add_user_plan_columns.py --db lucy.sqlite3`

### ✅ `validate_robots.py`

**Status:** Enforces crawl discipline (Oct 2025 refresh)

- Confirms every locale robots file allows homepages + hreflang
  alternates, blocks unrelated locales, blocks `/*?q=` and `/*/*/`, and
  links the correct sitemap.
- Usage:
  `python3 scripts/validate_robots.py [--langs xx yy zz]`

### 🆕 `validate_enhanced_locales.py`

**Status:** New validation script

- Validates that all locales have proper enhanced content:
  - Localized meta.title, meta.description, meta.keywords
  - Valid structured.json with aiSemantic arrays
  - SEO-optimized description length (140-160 characters)
- Usage:
  `python3 scripts/validate_enhanced_locales.py`

### 🆕 `validate_locale_keys.py`

**Status:** Frontend coverage audit

- Scans the frontend for translator usages and reports missing keys per
  locale
- Supports `--strict` to fail CI when translations lag behind code
- Usage:
  `python3 scripts/validate_locale_keys.py [--strict]`

### 🆕 `update_structured_data.py`

**Status:** Structured metadata synchronisation

- Mirrors each locale's `meta.title`, `meta.description`, and `meta.keywords`
  into `structured.json`
- Rebuilds the `aiSemantic` array and removes SearchAction URLs to avoid
  Search Console noise
- Usage:
  `python3 scripts/translations/update_structured_data.py`

### 🆕 `run_cro_smoke.py`

**Status:** Planned (Oct 2025)

- Headless browser smoke suite that visits `/pricing`,
  `/billing/credits`, and executes a search to verify loaders,
  overlays, and CTA analytics events.
- Emits a JSON report consumed by the deployment checklist.
- Usage (once implemented):
  `python3 scripts/run_cro_smoke.py --base-url https://staging.lucy.world`

## Current Localization Status

The Lucy World platform has **89 fully localized languages** with:

- ✅ Translated UI strings in `locale.json`
- ✅ Localized meta content (title, description, keywords)
- ✅ Enhanced `structured.json` with market-specific SEO data
- ✅ 6-item aiSemantic arrays for each market
- ✅ 140-160 character SEO-optimized descriptions

## Safe Workflow

1. **Validate current state**:
  `python3 scripts/validate_enhanced_locales.py`
1. **Verify translator coverage**:
  `python3 scripts/validate_locale_keys.py --strict`
1. **Synchronise structured metadata**:
  `python3 scripts/translations/update_structured_data.py`
1. **Generate essential assets**:
  `python3 scripts/generate_site_assets.py`
  - Preserves enhanced `structured.json` files
  - Creates robots.txt and sitemap.xml for new locales only
1. **Run CRO smoke tests** (when available):
  `python3 scripts/run_cro_smoke.py --base-url <env>` to confirm search
  loaders, pricing page, and overlays operate across locales.

## Dangerous Operations

⚠️ **Never run these on existing translations:**

- `generate_locales_from_en.py` without understanding the risks
- `generate_site_assets.py --force` (will overwrite enhanced content)
- `ensure_locale_meta.py` before the update (old version would overwrite)

## Adding New Languages

1. Add language code to `languages/languages.json`
2. Run: `python3 scripts/generate_language_registry.py`
3. Run: `python3 scripts/generate_locales_from_en.py --codes "xx" --i-understand-this-will-overwrite-translations`
4. Manually translate the new locale.json file
5. Create enhanced structured.json with localized content
6. Run: `python3 scripts/validate_enhanced_locales.py` to verify
7. Update CRO translation keys (CTA copy, overlays) and re-run
  `scripts/run_cro_smoke.py` once implemented.
