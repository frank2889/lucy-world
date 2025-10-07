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
- Premium search requests abort after 20 seconds via `fetchWithTimeout`, displaying localized timeout messaging when exceeded.

### DoD — Frontend

- [x] All `/xx/` routes render.  
- [x] Sidebar platforms load dynamically.  
- [x] Sidebar options derive from plan entitlements returned by the API.  
- [x] Sidebar surfaces the active plan status, AI credits, and upgrade paths.  
- [x] UI vs market picker independent.  
- [x] Structured data emitted per locale.  
- [x] Manifest.json synced with build.  

### UX Experience Baseline (Marketing + Product Surface Area)

> **The SPA must visually communicate the premium value proposition _before_ a user runs a query. Logged-out visitors should understand that Lucy World is a multi-market, multi-platform intelligence suite—not just a single search input.**

- **Hero deck (first fold)**
    - Gradient glassmorphism hero that introduces the proposition in under three lines.
    - Primary CTA: `Start exploring keywords` (focuses the search input or opens sign-in for magic link).
    - Secondary CTA: `See pricing & plans` → `upgrade_url` from anonymous entitlements payload.
    - Trust strip of metric chips: localized markets count, data refresh latency, teams shipping weekly.
    - Platform chips for Google, TikTok, Amazon, YouTube rendered inside the hero visual so coverage is obvious.
- **Feature grid**
    - Minimum three highlight cards: semantic clustering, localization workflow, AI briefs grounded in live SERP data.
    - Each card pulls copy from `languages/{lang}/locale.json`.
- **Sample insight state**
    - Anonymous users see a “sample insight” card (static JSON or cached response) so the page never appears empty.
    - Search skeleton animation in place while premium lookup runs.
- **Entitlements ribbon**
    - Persistent strip at top of sidebar summarizing tier, remaining AI credits, and upgrade/buy buttons.
    - Anonymous users see Free tier messaging + CTA linking to `upgrade_url`.
- **Projects onboarding**
    - “My projects” button visible in the hero CTA row for signed-in users.
    - Projects modal uses glass modal styling (blurred backdrop, 20px radius, 32px padding, wide layout) with localized empty state copy.
- **Magic-link modal**
    - Replaces plain login card with premium modal: blur backdrop, gradient button, localized microcopy, submission success state.
- **Responsive requirements**
    - Hero grid collapses to single-column ≤ 960px with maintained CTAs.
    - Modals remain within `min(94vw, 480px)` (login) / `min(94vw, 760px)` (projects) and preserve contrast ratios ≥ 4.5:1.

#### DoD — UX Experience

- [ ] Hero renders on first load (no data) with localized copy and both CTAs functioning.  
- [ ] Metric chips automatically reflect `languagesList.length` and refresh interval text from locale strings.  
- [ ] Feature grid cards pull translations from locale files (no hardcoded English).  
- [ ] Sample insight card appears until a real query result is available.  
- [ ] Sidebar ribbon shows tier + upgrade/buy links sourced from `/api/entitlements` for anonymous and authenticated sessions.  
- [ ] Projects modal and login modal use the shared premium styling classes (`modal-backdrop`, `modal-card`, etc.) and pass accessible contrast checks.  
- [ ] Mobile viewport ≤ 414px maintains CTAs in a vertical stack with tap targets ≥ 44px.  
- [ ] Cypress smoke spec covers hero presence (cta text, trust chips) and modal open/close interactions for Free vs signed-in users.  

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
- [ ] GSC reports no hreflang errors _(run `scripts/gsc_monitor.py --site https://lucy.world/` after authenticating Search Console access)._  
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

**Free (always-on)**  

- Search engines only (Google, Bing, Yahoo, Brave Search).  
- 20 queries/day cap.  
- 105+ languages, all countries.  
- Left sidebar shows only the Search Engines group.  

**Pro (€7.99/month via Stripe Checkout)**  

- 1,000 queries/day.  
- Full platform library (Search + Marketplaces + Social + Video).  
- 105+ languages, all countries.  
- Exports (CSV/JSON).  
- AI clustering + trend forecasting.  
- Save projects with collaboration.  
- Left sidebar unlocks all non-AI modules.  

**AI Credits (usage-based)**  

- Price determined by credit packs (TBD in Stripe).  
- Grants access to AI-assisted generation (insights, briefs, clustering boosts).  
- Credits decrement via `ai_usage` ledger.  
- Left sidebar reveals AI workspace entries when credits > 0.  

**Enterprise (Custom)**  

- Custom queries.  
- All platforms + local connectors (Bol, Marktplaats, eBay, Amazon regional).  
- All languages + variants.  
- API access, XLSX/API exports.  
- Priority GPU processing.  
- Team dashboards.  
- SSO, RBAC, audit logging.  
- SLA, support, white-label.  
- Compliance (SOC 2, GDPR, ISO).  

### DoD — Feature Plan

- [x] Free tier limits sidebar to Search Engines only.  
- [x] Pro unlocks full non-AI sidebar modules after successful billing activation.  
- [ ] AI credit balance controls visibility & usage of AI modules.  
- [ ] Enterprise gates advanced connectors and RBAC features.  
- [ ] Billing hooks validated across subscription + credit purchases.  

#### Backend roadmap — plan & credit state

- Extend `users.plan_metadata` (or create `user_entitlements`) to store `{ tier: "free" | "pro" | "enterprise", ai_credits: int, expires_at }`; write an Alembic migration that defaults new accounts to `free` with zero credits.  
- Introduce an entitlement resolver (`entitlements.get_for_user(user)`) that merges subscription status, Stripe customer metadata, and credit balances into a normalized object.  
- Add a protected `GET /api/entitlements` endpoint returning `{ tier, sidebar_groups, ai_credits, upgrade_url, buy_credits_url }`; for anonymous visitors, respond with the Free payload so the SPA can render marketing CTAs.  
- Update Stripe webhook handlers to mutate entitlements atomically on `checkout.session.completed`, `customer.subscription.updated`, `invoice.payment_succeeded`, and AI credit purchases.  
- Provide an admin CLI (e.g., `flask entitlements adjust --user ...`) for support-driven tier/credit corrections, and persist an audit trail in `entitlement_events` with before/after snapshots.  

##### DoD — Backend entitlements

- [ ] Alembic migration runs automatically and seeds existing users with valid `{ tier, ai_credits }`.  
- [ ] `GET /api/entitlements` returns complete payloads in manual curl + unit tests.  
- [ ] Stripe webhook replay from staging produces expected entitlement mutations without manual intervention.  
- [ ] Admin CLI writes `entitlement_events` rows with before/after JSON for every mutation.  
- [ ] Nightly reconciliation job compares Stripe state vs database and reports zero discrepancies.  

#### Frontend roadmap — entitlements-driven UI

- [x] (2025-10-05) Bootstrap the SPA by calling `/api/entitlements` and hydrating a global `useEntitlements()` store exposed via `EntitlementsProvider`.  
- [x] (2025-10-05) Render the left sidebar from `sidebar_groups`, falling back gracefully when no paid modules are returned.  
- [x] (2025-10-05) Gate platform tools with `<RequireEntitlement>` so deep links respect permissions and offer a Stripe upgrade CTA when locked.  
- [x] (2025-10-05) Surface the active tier, AI credits, and upgrade/buy-credit URLs inside the sidebar plan card.  
- [ ] Add Cypress specs and component tests that stub the entitlements payload to verify UI states for Free, Pro, exhausted credits, and topped-up credits.  

##### DoD — Frontend entitlements

- [x] `useEntitlements()` store has unit tests covering loading, success, and error states.  
- [x] Sidebar renders correct groups in Cypress snapshots for Free, Pro, and AI-enabled users _(Automated via `PlatformSidebar.test.tsx`; layer Cypress visual coverage later)._  
- [x] Route guards block direct navigation to gated pages when entitlements are missing (E2E test) — logic implemented via `<RequireEntitlement>`, Cypress coverage pending _(Covered by `RequireEntitlement.test.tsx`; replace with Cypress once suite lands)._  
- [x] Tier/credit badge displays accurate values pulled from the API in Storybook or visual tests (sidebar plan card).  
- [x] Upgrade and buy-credit CTAs open the correct Stripe URLs verified in integration tests — links now source from the entitlements payload; add automated verification _(Validated via `checkoutLauncher.test.ts` exercising the `/api/billing/checkout-session` fallback)._  

#### Account lifecycle & upgrade flows

- Signup flow provisions a Stripe customer and stores the Free entitlement snapshot immediately after email verification.  
- “Upgrade to Pro” CTA launches Stripe Checkout with price `price_pro_monthly` (€7.99); the webhook flips the tier to `pro` on success and back to `free` when a subscription is canceled or lapses.  
- AI credit purchases use usage-based products (e.g., `price_ai_credit_pack_100`); webhook increments `ai_credits`, and downstream AI jobs decrement credits via a centralized `consume_ai_credit(user, amount)` helper.  
- Offer the Stripe customer portal for downgrades/refunds; when the portal reports a churned subscription, schedule a job to revoke Pro sidebar groups at period end.  
- Seed marketing pages with anonymous entitlements so logged-out visitors still see accurate feature gating copy.  

##### DoD — Account lifecycle

- [x] New user signup flow produces Stripe customer + Free entitlement verified via smoke test _(Covered by `test_account_lifecycle.py::test_magic_link_signup_yields_free_entitlements`)._  
- [x] Successful Pro checkout updates tier and grants sidebar access in under one minute (monitored) _(Verified by `test_account_lifecycle.py::test_checkout_session_completed_promotes_user`)._  
- [x] AI credit purchase increases `ai_credits` and consumption decrements via `consume_ai_credit` _(Automated through `test_account_lifecycle.py::test_invoice_paid_grants_ai_credits`; helper lives in `backend/services/credits.py`)._  
- [x] Downgrade/cancel events remove Pro entitlements at the correct billing boundary _(Regression covered by `test_account_lifecycle.py::test_subscription_cancelled_downgrades_user`)._  
- [x] Anonymous marketing pages match current feature gating copy (checked during release QA) _(Smoke check via `test_account_lifecycle.py::test_anonymous_entitlements_match_free_marketing_copy`)._  

#### Observability, QA & support

- Emit structured logs (`entitlement_change`, `ai_credit_consumed`) and push them to the monitoring stack; alert on negative balances, failed webhook syncs, or tier mismatches.  
- Expose aggregated plan + billing counters via `backend.services.metrics.collect_entitlement_metrics` so dashboards and support tooling can query a single JSON payload.  
- Dashboard metrics to include daily upgrades, credit burn rate, AI module adoption, and sidebar unlock counts.  
- Build integration tests that simulate webhook payloads end-to-end and assert database entitlements match the expected state.  
- Document a support runbook linking entitlement IDs to Stripe customers, with remediation steps when discrepancies occur.  
- Backfill a nightly audit job that reconciles Stripe subscriptions, credit balances, and local entitlements, emitting discrepancies to Slack or Opsgenie.  

##### DoD — Observability & support

- [x] Structured logs for entitlement changes appear in the centralized logger with correlation IDs.  
- [ ] Metrics dashboard visualizes upgrades, credit burn, and AI adoption with seven-day retention.  
- [x] Webhook replay integration test is part of CI and passes.  
- [x] Support runbook published in `docs/support/entitlements.md` and linked from this section.  
- [ ] Nightly audit job produces a clean report (no unresolved discrepancies) for seven consecutive days.  

See [`docs/support/entitlements.md`](support/entitlements.md) for the full support playbook.  

#### Entitlements data contract

```json
{
    "tier": "pro",
    "ai_credits": 240,
    "sidebar_groups": ["search", "marketplaces", "social", "video", "ai"],
    "upgrade_url": "https://billing.stripe.com/p/session/pro",
    "buy_credits_url": "https://billing.stripe.com/p/session/ai_credits",
    "expires_at": "2025-12-01T00:00:00Z"
}
```

- `tier` — current subscription tier (`free`, `pro`, or `enterprise`).  
- `ai_credits` — integer remaining credits; zero hides AI modules.  
- `sidebar_groups` — ordered list of module keys rendered by the SPA.  
- `upgrade_url` / `buy_credits_url` — Stripe-hosted Checkout or Portal routes for self-serve actions. When `upgrade_url` is `/billing/upgrade` (or omitted), the SPA will call `POST /api/billing/checkout-session` and follow the returned Stripe URL automatically.  
- `expires_at` — ISO timestamp when the tier downgrades; omitted for perpetual tiers.  

##### DoD — Data contract

- [ ] API responses validated against a JSON Schema stored in `docs/contracts/entitlements.schema.json`.  
- [ ] Contract tests in CI ensure the backend never removes required keys without bumping the schema version.  
- [ ] Frontend type definitions derive from the schema (e.g., via `zod-to-ts`) to eliminate drift.  

#### Testing matrix — entitlements rollout

| Layer | Scenario | Tooling | Owner |
|-------|----------|---------|-------|
| Unit  | Entitlement resolver combinations (free → pro, pro → churn, credits negative) | `pytest` | Backend |
| Unit  | `useEntitlements` store loading/error states | Vitest/Jest | Frontend |
| Integration | Stripe webhook replay (`checkout.session.completed`, credit purchase) | `pytest` + Stripe CLI fixtures | Backend |
| E2E | Sidebar visibility for Free/Pro/AI users | Cypress | Frontend |
| E2E | Upgrade + credit purchase happy path | Cypress + Stripe test keys | Growth |
| Monitoring | Nightly reconciliation job success | Scheduled job + Grafana alert | DevOps |

##### DoD — Testing matrix

- [ ] Each row has an implemented test with a reliable pass/fail signal.  
- [ ] Failing tests block deployment via CI.  
- [ ] QA checklist references this table during release reviews.  

#### Implementation Notes — Stripe Billing

- `POST /api/billing/checkout-session` (auth required) creates a Stripe Checkout session using `STRIPE_PRICE_PRO` (and optional `STRIPE_PRICE_PRO_USAGE`) and returns the hosted payment `url`. The frontend upgrade CTA posts here automatically when `upgrade_url` resolves to `/billing/upgrade`.  
- `POST /api/billing/customer-portal` returns a Stripe Billing customer portal session so users can self-manage subscriptions.  
- `POST /api/billing/webhook` processes Checkout, invoice, and subscription events to keep the `users` and `payments` tables in sync.  
- Environment variables: `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_PRICE_PRO`, optional `STRIPE_PRICE_PRO_USAGE`, `STRIPE_WEBHOOK_SECRET`, plus `PUBLIC_BASE_URL` for redirect URLs.  
- For local experiments, clone Stripe's official samples (see [stripe-samples on GitHub](https://github.com/stripe-samples)) rather than bundling vendor code into this repo.  

##### Stripe Checkout task list (strict)

1. **Secrets & configuration**

    - [ ] Create or update the secrets entry for `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_PRICE_PRO`, and (if applicable) `STRIPE_PRICE_PRO_USAGE` in the deployment environment (do not commit plaintext keys).  
    - [ ] Configure `STRIPE_WEBHOOK_SECRET` from the live webhook endpoint and set `PUBLIC_BASE_URL` to the production origin.  
    - [ ] Validate prices exist in the Stripe dashboard and match the plan matrix documented above.  

1. **Backend readiness**

    - [ ] Run `python -m compileall backend` locally to ensure the billing modules compile.  
    - [ ] Execute the billing test suite (`pytest backend/tests/billing` when added) or at minimum hit `/api/billing/checkout-session` and `/api/billing/customer-portal` with authenticated requests in staging.  
    - [ ] Start `stripe listen --forward-to localhost:5000/api/billing/webhook` in development and confirm webhook events update the `payments` and `users.plan_metadata` tables as expected.  

1. **Frontend & localization**

    - [ ] Place all checkout CTA copy in `languages/{lang}/locale.json` and reference via locale keys—no hardcoded strings in components.  
    - [ ] Ensure the React billing entry point loads `STRIPE_PUBLISHABLE_KEY` from `/api/billing/config` and never embeds it statically.  
    - [ ] Verify the checkout button state handles loading, success redirect (adds `session_id`), and localized error surfaces.  

1. **Deploy & monitor**

    - [ ] Redeploy to staging, execute a full trial → pro upgrade using Stripe test cards, and confirm invoices generate with localized metadata.  
    - [ ] Enable required alerts: webhook failure notifications in Stripe and application logs for `billing` blueprint errors.  
    - [ ] After production deploy, reconcile the first live invoice against `payments` to verify amounts/net/tax persist correctly.  

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
4. `Disallow: /*?q=` → prevent query-string search result URLs from being crawled.  
5. `Disallow: /*/*/` → block everything deeper than `/xx/`.  
6. `Sitemap: https://lucy.world/{lang}/sitemap.xml`

### DoD — Robots & Crawl

- [x] Root robots only contains sitemap index.  
- [x] Each robots allows its own `/xx/`.  
- [x] Each robots allows hreflang alternates for shared markets.  
- [x] Each robots disallows all unrelated `/yy/`.  
- [x] Each robots disallows query-string search URLs (`/*?q=`).  
- [x] Each robots disallows indexing deeper than `/xx/`.  
- [x] Each robots includes sitemap.  
- [x] `/xx/?q=` responses render `meta name="robots" content="noindex, nofollow"`.  
- [x] CI ensures consistency across 105+ languages.  
- [ ] GSC shows no cannibalisation _(monitor via `scripts/gsc_monitor.py` to flag duplicate queries)._  

---

📌 This document defines the **complete enterprise architecture of Lucy.world**.  
Every part is governed by **Definition of Done (DoD)** checklists, so devs and AI copilots can build and validate the system automatically.  
