# Lucy.world Changelog

## 2025-10-08 (Language Equality & Clean Design Philosophy)

### Added — Translation System Overhaul

- **Zero fallback architecture** - Removed ALL language fallbacks. Every language is self-contained.
- **Missing translation markers** - Show `[MISSING: key]` instead of English text when translations are incomplete.
- **Complete Dutch entitlements** - Added all `entitlements.*` translation keys to Dutch locale.
- **SMTP email integration** - Configured Gmail SMTP for magic link authentication via DigitalOcean environment variables.

### Changed — Frontend Architecture

- Removed `uiFallback` state completely from App.tsx
- Updated `createTranslator()` to only use current language, never fallback to another
- Removed `uiFallback` from `PlatformToolProps` interface
- Updated all 18 platform tools (Google, DuckDuckGo, Bing, Amazon, etc.) to use single-language approach
- Fixed hardcoded English string in timeout error handler

### Fixed — Language System

- Translation keys no longer flicker during load - each language stands alone
- English, Dutch, and all other languages treated equally - no priority
- Incomplete translations immediately visible with `[MISSING: key]` placeholders
- Removed final hardcoded English fallback: "The search took too long. Please try again."

### Documentation — Design Philosophy

- **NEW:** Created `docs/DESIGN.md` with Lucy World's clean, professional design philosophy
- **Core principle:** Daily-use business tool, not flashy marketing site
- **Guidelines:** No gradients, minimal animations, flat surfaces, data-first layouts
- **Enterprise focus:** Reliability, clarity, consistency over novelty
- **Anti-patterns documented:** What NOT to do (consumer app styling, trendy effects, etc.)

### Technical Standards Established

- **Translation rule:** Every user-facing string MUST be in locale files, no hardcoded text
- **Design rule:** Clean and functional over decorative and flashy
- **Loading states:** Skeleton loaders only, no fancy spinners
- **Color usage:** WCAG AA minimum contrast (4.5:1 for body text)
- **Spacing system:** 8px base unit grid

## 2025-10-08 (Frontend-Backend Integration & Billing UX)

### Added — Billing & Entitlements UI

- **Inline plan summary cards** in both desktop header and mobile topbar showing tier, AI credits, renewal date, and workspace unlock status.
- **Billing action buttons** (Upgrade plan, Get AI credits) displayed in both desktop and mobile layouts with proper loading states.
- **Sticky CTA component** that appears for non-signed-in users and users with low credits (<25), with session-based dismissal.
- **Credit pack pricing integration** from `/api/billing/credit-packs` endpoint with formatted prices in user's locale.
- **Checkout flow handlers** for both plan upgrades (`/api/billing/upgrade-checkout`) and credit purchases (`/api/billing/credit-checkout`).
- **Top-bar layout refactor** consolidating plan/billing controls into consistent mobile and desktop UX.

### Changed — Frontend Architecture

- `App.tsx` now renders `renderPlanSummary()` and `renderBillingActions()` helper functions for both mobile and desktop contexts.
- Entitlements hook (`useEntitlements`) integrated throughout the component tree with proper loading/error states.
- Session storage used for sticky CTA dismissal to avoid localStorage pollution.
- Credit pack price formatting respects user's UI language for currency display (nl-NL, en-US, etc.).
- Low credits threshold set to 25 AI credits with automatic CTA re-showing when threshold crossed.

### Fixed — Payment Integration

- Credit checkout now properly validates `price_id` before initiating Stripe session.
- Upgrade checkout handles missing `upgrade_url` gracefully with localized error messages.
- Both checkout flows set proper loading states to prevent double-clicks.
- Token expiry handling improved for 401 responses from billing endpoints.

### Documentation — Current Session

- Updated CHANGELOG.md with comprehensive billing UI integration details.
- Documented frontend-backend contract for `/api/billing/credit-packs` and checkout endpoints.
- Added session state management patterns for CTA dismissal and checkout flows.

### Technical Debt Identified

- Frontend bundle may not be rebuilt after recent App.tsx changes - requires `npm run build` in `frontend/` directory.
- Backend deployment may need restart to serve updated static assets from `static/app/`.
- GitHub Actions deployment workflow may require manual trigger or new commit to deploy latest changes.

## 2025-10-07 (UX & CRO sweep)

### Added — Conversion surfaces

- Documented the `/pricing` page contract, Premium overlay, sticky sidebar CTA, and localized copy requirements in `ARCHITECTURE.md`.
- Captured the CRO deployment ritual and route verification steps in `DEPLOYMENT-GUIDE.md`.
- Logged analytics + experimentation expectations (Optimizely/VWO) and Sentry locale tagging strategy in the architecture blueprint.

### Changed — Documentation

- `docs/README.md` now surfaces the CRO checklist so every deploy captures UX learnings.
- Refreshed localization docs (`languages/README.md`, `markets/README.md`, `languages/nl/README.md`) to emphasise Dutch defaults without regressing other locales.
- Added support notes for Stripe credit packs + pricing redirects to `docs/support/entitlements.md`.

### Testing — Pending

- Browser smoke tests for `/pricing`, `/billing/credits`, loader animation, and Premium overlay planned (add to QA pipeline).
- Optimizely/VWO integration and analytics schema validation TODO before release cut.

## 2025-10-07

### Added — Observability

- Entitlement metrics aggregation service (`backend/services/metrics.py`) that produces plan, trial, and revenue counters for observability dashboards.
- Backend unit coverage (`backend/tests/test_metrics.py`) validating trial expiry buckets and payment rollups.

### Documentation — Observability

- Updated architecture observability section to reference the metrics service JSON payloads.
- Expanded support runbook with a quick metrics sampling command for on-call engineers.

### Testing — Observability

- `python3 -m pytest backend/tests/test_metrics.py` — passes (new coverage).

## 2025-10-06

### Added

- Structured logging utilities that assign per-request correlation IDs and emit `entitlement_change` / `ai_credit_consumed` events.
- Support runbook at `docs/support/entitlements.md` covering investigation, remediation, and webhook replay steps.
- Stripe webhook replay integration test ensuring `invoice.paid` events mutate plans and credits correctly.

### Changed

- Locale asset handler now streams files from memory to avoid lingering file handles and warning noise during tests.
- Documentation (`ARCHITECTURE.md`, `README.md`) updated to reflect the new logging, testing, and support coverage.

### Testing

- `python3 -m pytest -W default` (backend) — 13 tests, pass, zero warnings.
- `npm test` (frontend) — 23 tests, pass.
