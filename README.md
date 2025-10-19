# Lucy World

Multilingual, privacy-first keyword intelligence platform built with a Flask
backend and a Vite-powered React frontend. This repository centralizes the app
code, localization assets for more than 100 languages, the design system
sources, and deployment tooling.

## Project Status

- Definition of Done progress: 17 / 70 tasks complete (24.3%).
- Current focus: analytics schema, Cypress smoke coverage, search
   dispatcher contract tests, and enterprise gating.
- Deep history and blockers live in `docs/PROGRESS.md` and the changelog.

## Stack Overview

- **Frontend**: React 18 + Vite 7, TypeScript strict mode, localized routing
   per language.
- **Backend**: Flask with Gunicorn, SQLite (dev) / Postgres (prod), Stripe
   billing integration, Redis-compatible caching layer.
- **Automation**: `auto-deploy.sh`, optional GitHub Actions workflow
   (`.github/workflows/deploy-digitalocean.yml.disabled`), and
   `scripts/webhook.py` for self-hosted deployments.
- **Design System**: Token and theme generation driven from
   `design/design.md`.
- **Localization**: `languages/` directory with locale bundles, structured
   metadata, robots, and sitemaps.

## Getting Started

1. Install prerequisites: Node 20+, npm 10+, Python 3.11+ (project targets
    3.13), and a working virtualenv tool.
2. Copy `env.example` to `.env` and supply required secrets (Stripe, SMTP,
   etc.). Keep `CACHE_DISABLED=true` if you want to mirror the current
   production posture of running without in-process caches.
3. Create a virtual environment and install backend dependencies.

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

4. Install frontend dependencies and start the dev server.

    ```bash
    cd frontend
    npm install
    npm run dev
    ```

5. In another terminal, run the Flask app (example).

    ```bash
    flask --app backend.app run
    ```

See `docs/DEPLOYMENT-GUIDE.md` for the full deployment ritual, CRO acceptance
pass, and production hardening steps.

## Localization & Content Guardrails

- Every user-facing string must live in `languages/{code}/locale.json`; no
   hardcoded fallbacks are allowed.
- After changing `meta.title`, `meta.description`, or `meta.keywords`, run
   `python3 scripts/translations/update_structured_data.py` to keep
   `structured.json` in sync.
- Use `scripts/validate_locale_keys.py --strict` and
   `scripts/validate_enhanced_locales.py` during translation sweeps.
- Detailed rules live in `docs/TRANSLATION_RULES.md` and `languages/README.md`.

## Deployment Summary

- `auto-deploy.sh` is the canonical deployment script; install it on the server
   as `/usr/local/bin/auto-deploy-lucy`.
- Re-enable the GitHub Actions workflow by renaming
   `deploy-digitalocean.yml.disabled` after secrets are configured.
- Optional self-hosted webhook runs from `scripts/webhook.py` on port 9000.
- Troubleshooting tips, systemd units, TLS renewals, and Nginx guidance are in
   `docs/DEPLOYMENT-GUIDE.md`.

## Key Documentation

- `docs/ARCHITECTURE.md`: architecture, API contracts, observability, Definition
   of Done.
- `docs/DEPLOYMENT-GUIDE.md`: provisioning, automation, CRO acceptance
   workflow, troubleshooting.
- `docs/BILLING-INTEGRATION.md`: Stripe configuration, entitlements flows,
   manual remediation.
- `docs/CHANGELOG.md`: release notes and dated updates.
- `docs/PROGRESS.md`: Definition of Done progress tracker and session notes.
- `docs/TRANSLATION_RULES.md`: localization standards, enforcement tiers,
   validation checklist.
- `docs/SMTP_SETUP.md`: Gmail SMTP app-password setup instructions.
- `docs/support/entitlements.md`: support runbook for entitlements and credit
   investigations.
- `design/design.md`: canonical design specification that generates tokens and
   themes.
- `scripts/README.md`: maintenance and validation tooling overview.
- `languages/README.md`: directory structure and translation workflow
   expectations.
- `markets/README.md`: market-level hreflang, CRO, and payment configuration
   guidance.

## Repository Layout Highlights

- `backend/`: Flask application, blueprints, models, services, integration
   tests.
- `frontend/`: React SPA, Vite config, styles, and platform tool components.
- `scripts/`: Maintenance utilities (localization, deployment, migrations);
   treated as a package for backend imports.
- `design/`: Authoritative design system sources and generated artifacts.
- `docs/`: In-depth guides referenced above.
- `languages/` and `markets/`: Localization and market metadata consumed by the
   app.

## Operations & Support

- Stripe entitlements troubleshooting: `docs/support/entitlements.md`.
- SMTP credential rotation: `docs/SMTP_SETUP.md`.
- Deployment triggers archived under `.github/deploy-trigger-*.md` for audit
   history.

For additional context or historical decisions, review `docs/CHANGELOG.md` and
the dated entries in `.github/`.
