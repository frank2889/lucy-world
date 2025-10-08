# Lucy.world Changelog

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
