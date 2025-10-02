# Localization & SEO Overview

- The backend enforces language-prefixed URLs such as `/en/` or `/nl/`. The bare `/` route redirects to the detected language via `_detect_lang()`, and only locales with real JSON dictionaries are exposed under `/meta/locales.json`.
- `_spa_response()` builds canonical and `hreflang` links for every available locale, plus an `x-default` pointing to `/`. Each localized request also emits `<meta name="robots" content="index, follow">` unless a locale JSON overrides `meta.robots`.
- `/meta/content/<lang>.json` loads from `languages/<lang>/locale.json`. A language is considered live only when that file exists, providing UI copy (`strings`) plus optional SEO fields (`meta.title`, `meta.description`, `meta.keywords`, `meta.robots`).
- The React app keeps UI language (URL + sidebar menu) independent from the search request language/country selectors. Geo defaults come from `/meta/detect.json`, while subsequent choices persist in `localStorage`.
- Search POSTs send both `language` and `country` to `/api/free/search`, so keyword data respects the user-selected market regardless of the interface locale.
