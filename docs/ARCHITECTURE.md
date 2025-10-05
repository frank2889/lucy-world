# Lucy.world — Enterprise Architecture & Global DoD

Lucy.world is a **multilingual, privacy-first keyword intelligence SaaS**.  
This document is the **single source of truth**. It defines languages, markets, APIs, SEO, growth strategies, billing, costs, robots discipline, and growth flywheel — with **Definition of Done (DoD)** checklists for every stage.

---

## 1. Domain & Language Authority Strategy

- Root (`https://lucy.world/`) is **x-default only**.  
- Root never ranks and always redirects to a language path.  
- **No canonical, structured data, or language content exists at `/`**.  
- **All authority belongs to language paths**: `/nl/`, `/de/`, `/fr/`, etc.  
- **No language references in code**: all UI/meta strings live only in `languages/{lang}/locale.json`.  
- **Markets folder** defines hreflang per country, tied directly to language files.  
- Each `/xx/` behaves as a standalone localized site with its own sitemap, robots, and structured data.

> **AI Agent TODO (Always Enforce)**

### DoD — Domain & Language

- [x] Root = x-default only, always redirect to locale.  
- [x] Canonical tags always point to `/xx/`.  
- [x] No language strings outside `languages/{lang}/locale.json` (enforced by `scripts/validate_locale_keys.py`).  
- [x] Each locale generates robots.txt, sitemap.xml, structured.json.  
- [x] CI: `validate_enhanced_locales.py` passes for all locales.  

---

## 2. Languages (ISO-639-1 Codes)

> **AI Agent TODO (Always Enforce)**

Supported (from `languages/languages.json`):

`af, sq, am, ar, hy, az, eu, be, bn, bs, bg, my, ca, zh, co, hr, cs, da, nl, en, eo, et, fi, fr, fy, gl, ka, de, el, gu, ht, ha, he, hi, hu, is, ig, id, ga, it, ja, jv, kn, kk, km, rw, ko, ku, ky, lo, la, lv, lt, lb, mk, mg, ms, ml, mt, mi, mr, mn, ne, no, ny, or, ps, fa, pl, pt, pa, ro, ru, sm, gd, sr, st, sn, sd, si, sk, sl, so, es, su, sw, sv, tl, tg, ta, tt, te, th, tr, tk, uk, ur, ug, uz, vi, cy, xh, yi, yo, zu`

### DoD — Languages

- [x] `/xx/` homepage renders for each supported language.  
- [x] `languages/{xx}/locale.json` exists with UI + meta.  
- [x] Canonical + hreflang tags generated.  
- [x] Locale included in sitemap.  
- [x] RTL (ar, he, fa, ur) styled correctly.  
- [x] CJK (zh, ja, ko) fonts render correctly.  

---

## 3. Countries & Markets (ISO 3166-1 Alpha-2)

- `/markets/{CC}/hreflang.json` defines default + alternates.  
- `/markets/index.json` enumerates all ISO countries (full coverage).  
- Each market links only to valid `languages/{xx}/locale.json`.

### DoD — Markets

- [x] All ISO countries covered in `/markets/`.  
- [x] Each `/markets/{CC}/hreflang.json` references existing locales only.  
- [x] No orphan hreflang entries.  
- [x] Default locale for each market exists in `/languages/`.  
- [x] x-default always points to root.  

---

## 4. APIs

**Public APIs**  

- `POST /api/free/search` → `{ keyword, language, country }`  
- `GET /meta/detect.json` → detected locale  
- `GET /meta/content/<lang>.json` → UI + SEO strings  
- `GET /meta/languages.json` → language list  
- `GET /meta/locales.json` → locale mappings  
- `GET /meta/countries.json` → country list  
- `GET /meta/markets.json` → country → locale mapping  
- `GET /meta/sitemap.xml` → sitemap index  

**Authenticated APIs**  

- `POST /api/projects` → save project with `name, description, language, country, data`

### DoD — APIs

- [x] `/meta/*` endpoints return valid JSON.  
- [x] Free search supports all languages + countries.  
- [x] Invalid ISO codes rejected with 400.  
- [x] Projects API persists securely.  
- [x] Health probes (`/meta/detect.json`, `/api/free/search`) return 200.  

---

## 5. Frontend (React + Vite SPA)

- Locale routing = `/xx/`.  
- UI language vs. market language selection are independent.  
- Sidebar includes platforms (Google, Yahoo, Brave, YouTube, App Store, Amazon, etc.).  
- Built with Vite, hashed asset filenames in `manifest.json`.  
- Metadata and UI localized via `locale.json`.

### DoD — Frontend

- [x] All `/xx/` routes render.  
- [x] Sidebar platforms load dynamically.  
- [x] UI vs market picker independent.  
- [x] Structured data emitted per locale.  
- [x] Manifest.json synced with build.  

---

## 6. Backend (Flask + Gunicorn + Nginx)

- Entrypoint: `backend.create_app()`.  
- Database: SQLite (dev) / Postgres (prod).  
- Gunicorn + Nginx + systemd orchestration.  
- Auto-deploy via `webhook.py` + `auto-deploy.sh`.  
- Logging via journalctl, curl probes, Certbot renewals.  
- `scripts/monitor_gunicorn_service.py` performs systemd and HTTP smoke checks.  
- `scripts/renew_tls.sh` runs certbot renewals and reloads Nginx/Gunicorn.  

### DoD — Backend

- [x] Gunicorn service stable.  
- [x] Env vars normalized (`postgres://` → `postgresql://`).  
- [x] Auto-deploy works on push.  
- [x] Health check `/meta/detect.json` = 200.  
- [x] TLS auto-renewed.  

---

## 7. Internationalization & SEO

- Hreflang reciprocity enforced.  
- Sitemap index includes all `/xx/` roots.  
- Structured data localized per `locale.json`.  
- Robots generated per language.  

### DoD — Internationalization & SEO

- [x] Every `/xx/` emits canonical + hreflang block.  
- [x] Root `/sitemap.xml` valid and complete.  
- [ ] GSC reports no hreflang errors *(run `scripts/gsc_monitor.py --site https://lucy.world/` after authenticating Search Console access).*  
- [x] Structured data validates per locale.  
- [x] Robots.txt points to sitemap index.  

---

## 8. Growth Flywheel — Keyword-to-Blog

- User queries scored for audience potential.  
- 95–100% potential queries flagged.  
- Threshold (≥ 10 users or ≥ 50 searches/day) required.  
- Flagged queries logged in candidate DB.  
- AI pipeline generates blog draft.  
- Draft published as blog/insight page.  
- Content ranks → attracts users → generates more queries → loop.  

### DoD — Growth Flywheel

- [x] Backend logs queries + scores.  
- [x] Aggregation thresholds enforced.  
- [x] Candidate DB exists.  
- [x] AI pipeline generates draft blogs.  
- [x] Drafts stored as Markdown/HTML.  
- [x] Publishing workflow operational.  
- [x] Privacy policy updated.  
- [x] Blog listed in sitemap.  
- [x] Flywheel verified.  

---

## 9. Feature Plan Matrix

**Free Trial (14d)**  

- 20 queries/day  
- Google only  
- 105+ languages  
- All countries  

**Pro (€7.99/month via Stripe Checkout)**  

- 1,000 queries/day  
- All platforms  
- 105+ languages  
- All countries  
- Exports (CSV/JSON)  
- AI clustering  
- Trend forecasting  
- Save projects  

**Enterprise (Custom)**  

- Custom queries  
- All platforms + local connectors (Bol, Marktplaats, eBay, Amazon regional)  
- All languages + variants  
- API access, XLSX/API exports  
- Priority GPU processing  
- Team dashboards  
- SSO, RBAC, audit logging  
- SLA, support, white-label  
- Compliance (SOC 2, GDPR, ISO)  

### DoD — Feature Plan

- [x] Trial expires after 14 days.  
- [x] Trial → Pro conversion via Stripe Checkout.  
- [x] Pro unlocks exports, clustering, projects.  
- [ ] Enterprise gates advanced features.  
- [ ] Billing hooks validated.  

#### Implementation Notes — Stripe Billing

- `POST /api/billing/checkout-session` (auth required) creates a Stripe Checkout session using `STRIPE_PRICE_PRO` (and optional `STRIPE_PRICE_PRO_USAGE`) and returns the hosted payment `url`.  
- `POST /api/billing/customer-portal` returns a Stripe Billing customer portal session so users can self-manage subscriptions.  
- `POST /api/billing/webhook` processes Checkout, invoice, and subscription events to keep the `users` and `payments` tables in sync.  
- Environment variables: `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_PRICE_PRO`, optional `STRIPE_PRICE_PRO_USAGE`, `STRIPE_WEBHOOK_SECRET`, plus `PUBLIC_BASE_URL` for redirect URLs.  
- A reference implementation lives in `docs/examples/stripe-checkout/` alongside the official Stripe sample.  

---

## 10. Costs & Margins

- Infra: €100–200/month early, <€1,000/month scaled.  
- Stripe fees: 2.9% + €0.30 per txn (varies per region).  
- 1,000 Pro users (€7.99) → ~€7,200 net MRR.  
- 5,000 Pro users → ~€36,000 net MRR.  
- Enterprise accounts multiply revenue with negligible infra cost.  

### DoD — Costs & Margins

- [ ] Costs tracked monthly.  
- [ ] Stripe fees logged.  
- [ ] Growth tracked MRR vs infra vs fees.  

---

## 11. Robots.txt, Sitemaps & Crawl Discipline

### Rules

- Root robots.txt contains only:  
  `Sitemap: https://lucy.world/sitemap.xml` (sitemap index).  
- Each `/languages/{lang}/robots.txt` controls that locale.

### Per-language Robots

1. `Allow: /{lang}/`  
2. Allow valid hreflang alternates for shared markets (from `/markets/{CC}/hreflang.json`).  
3. `Disallow: /{yy}/` for all other language roots not listed as alternates.  
4. `Disallow: /*/*/` → block everything deeper than `/xx/`.  
5. `Sitemap: https://lucy.world/{lang}/sitemap.xml`

### DoD — Robots & Crawl

- [x] Root robots only contains sitemap index.  
- [x] Each robots allows its own `/xx/`.  
- [x] Each robots allows hreflang alternates for shared markets.  
- [x] Each robots disallows all unrelated `/yy/`.  
- [x] Each robots disallows indexing deeper than `/xx/`.  
- [x] Each robots includes sitemap.  
- [x] CI ensures consistency across 105+ languages.  
- [ ] GSC shows no cannibalisation *(monitor via `scripts/gsc_monitor.py` to flag duplicate queries).*  

---

📌 This document defines the **complete enterprise architecture of Lucy.world**.  
Every part is governed by **Definition of Done (DoD)** checklists, so devs and AI copilots can build and validate the system automatically.  
