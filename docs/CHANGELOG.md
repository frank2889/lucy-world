# Lucy.world Changelog

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
