# Lucy World – Global i18n rollout checklist

This checklist tracks everything needed to support all languages worldwide using language-only URLs (e.g., /en/, /nl/, /de/), correct hreflang, and scalable translation/dictionary infrastructure.

## ✅ Current status

- [x] Language-only URLs with server-side detection and redirect from `/` → `/<lang>/` (Accept-Language)
- [x] Vite manifest wired to server template for hashed assets
- [x] Canonical + hreflang generation for all supported languages
- [x] `x-default` hreflang to `/`
- [x] Global language source: `languages/languages.json`
- [x] Sitemap includes a homepage per language
- [x] Country selector uses flags; full Google language list available
- [x] Frontend i18n basic wiring with EN/NL and fallback to EN

## 1) Language inventory (source of truth)

- File: `languages/languages.json`
- The backend reads this and normalizes to primary codes for URLs (/zh/ for zh-CN/zh-TW). Update this list to add/remove languages.

Languages included (primary codes used for URLs):

- af, sq, am, ar, hy, az, eu, be, bn, bs, bg, my, ca, ceb, zh, co, hr, cs, da, nl, en, eo, et, fi, fr, fy, gl, ka, de, el, gu, ht, ha, haw, he, hi, hmn, hu, is, ig, id, ga, it, ja, jv, kn, kk, km, rw, ko, ku, ky, lo, la, lv, lt, lb, mk, mg, ms, ml, mt, mi, mr, mn, ne, no, ny, or, ps, fa, pl, pt, pa, ro, ru, sm, gd, sr, st, sn, sd, si, sk, sl, so, es, su, sw, sv, tl, tg, ta, tt, te, th, tr, tk, uk, ur, ug, uz, vi, cy, xh, yi, yo, zu

Note: We normalize variants to primary (e.g., zh-CN/zh-TW → zh). If we later want distinct /zh-cn/ vs /zh-tw/ URLs, we can switch to regioned paths.

## 2) Backend: routing and SEO

- [x] Detect language via `Accept-Language`
- [x] Redirect `/` → `/<lang>/`
- [x] Render `templates/base_spa.html` with canonical + hreflang for all languages
- [x] Add `x-default` hreflang → `/`
- [x] `/meta/sitemap.xml` enumerates `/<lang>/` for all languages
- [ ] Optional: add `/robots.txt` alias to `/meta/robots.txt`
- [ ] Optional: add Cache-Control headers for `/meta/*` (24h) and ETag
- [ ] Optional: per-language sitemaps if we add many internal routes later

## 3) Frontend: i18n implementation

- [ ] Create translation files for all languages: `frontend/src/i18n/<code>.json`
	- Seed with auto-translation; human review later
	- Include keys already used in `App.tsx` (search, nav, KPIs) and any new UI copy
- [ ] Implement dynamic loading for translations (import or fetch json by URL code)
	- Fallback to `en` if missing
	- Handle loading state gracefully
- [ ] Locale-aware formatting
	- Use `Intl.NumberFormat(lang)` and `Intl.DateTimeFormat(lang)` for numbers/dates
	- Replace the current fixed `nl-NL` formatter with the detected lang
- [ ] RTL support
	- Add `dir="rtl"` when lang in [ar, he, fa, ur]
	- Verify spacing/mirroring in CSS
- [ ] Fonts and typography
	- Ensure font fallback covers CJK (zh, ja, ko), Thai (th), Arabic (ar)
	- Verify glyph coverage and line-height
- [ ] Language switcher
	- Add a simple switcher in the sidebar to navigate between `/<lang>/`

## 4) Dictionaries (future advanced features)

- Structure: `languages/dictionaries/<code>.json`
- Contents: stopwords, synonyms, stemming rules, locale-specific patterns
- [ ] Create stub files for each language
- [ ] Define a minimal schema (e.g., `{ "stopwords": [], "synonyms": {"a":"b"} }`)
- [ ] Wire into advanced analysis when ready

## 5) Country / language selection UX

- [x] Country as flags (ISO 3166-1 alpha-2)
- [x] Google languages list available
- [ ] Optional: filter languages by country (when relevant)
- [ ] Optional: auto-detect country (GeoIP) to default the flag

## 6) Analytics

- [ ] Add GA4 (or your chosen analytics)
	- Set user property `lang = document.documentElement.lang`
	- Include event param `lang` on key events/searches
	- Slice reports by path prefix and/or lang property

## 7) QA and SEO validation

- [ ] Smoke-test `/<lang>/` loads for all languages (scripted)
- [ ] Validate canonical + hreflang tags (spot-check and via Search Console)
- [ ] Lighthouse checks for a11y and performance on RTL/CJK pages
- [ ] Ensure redirects and caching work in production

## 8) Deployment and performance

- [ ] Confirm build pipeline includes all i18n files
- [ ] Consider code-splitting translations to keep main bundle lean
- [ ] Add basic monitoring for missing translations (log when fallback used)

## 9) Content process

- [ ] Establish translation workflow (MT bootstrap → human review)
- [ ] Maintain a glossary for SEO terms (per language)
- [ ] Schedule periodic updates

---

## Deliverables per language (definition of done)

- [ ] `/<lang>/` renders with that language
- [ ] `<link rel="alternate" hreflang="<lang>">` present
- [ ] Translation file exists and loads without fallback
- [ ] Dictionary stub exists (even if empty)
- [ ] Numbers/dates formatted via `Intl` for `<lang>`
- [ ] RTL/CJK specifics addressed where applicable

## Notes

- We currently use language-only URLs for simplicity and strong SEO signals. If we need regional variants (e.g., `pt` vs `pt-BR`), we can evolve to regioned paths and expand the hreflang map accordingly.
- The sitemap currently lists only the language homepages. As we introduce more pages, we’ll generate language-specific entries for them too.
```
../TODO.md
