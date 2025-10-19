# Documentation Hub

The project overview, status, and quick-start instructions now live in the
repository root `README.md`. This file tracks documentation conventions and
provides pointers for maintaining the guides under `docs/`.

## Authoring Guidelines

- Keep lines under 80 characters and format fenced code blocks with blank lines
  above and below.
- Reference source files with relative paths (for example,
  `scripts/auto-deploy.sh`).
- When instructions duplicate across guides, push the canonical wording into
  the root `README.md` or a single markdown file and link to it here.
- Include change dates in headings when adding new operational rituals or
  processes.

## Filing Content

- Architecture, APIs, observability, and Definition of Done:
  `docs/ARCHITECTURE.md`.
- Deployment workflows, automation, and troubleshooting:
  `docs/DEPLOYMENT-GUIDE.md`.
- Billing and Stripe onboarding: `docs/BILLING-INTEGRATION.md`.
- Release notes: `docs/CHANGELOG.md`.
- DoD plan and session tracking: `docs/ARCHITECTURE.md` and `docs/PROGRESS.md`.
- Localization standards: `docs/TRANSLATION_RULES.md` (with supporting
  workflows in `scripts/README.md`).
- SMTP setup and credential rotation: `docs/SMTP_SETUP.md`.
- Support runbooks: `docs/support/entitlements.md` (add more under
  `docs/support/` as needed).

## Updating Status Sections

- Refresh the high-level project status in `README.md` after major milestones.
- Append dated entries to `docs/CHANGELOG.md` rather than creating new summary
  files.
- When creating new documentation, add a brief pointer here so contributors can
  discover it quickly.
