# Lucy World documentation hub

Lucy World Search is a privacy-first, multi-locale keyword research product. The backend serves a single-page React app, automatically negotiates the visitor language from `Accept-Language`, and proxies keyword research requests to the free tool pipeline. This directory keeps the living documentation for everything around the product, infra, and operations.

## Product snapshot — October 2025

- Multi-locale SPA routed via `/&lt;lang&gt;/…` with canonical and `hreflang` metadata emitted server-side.
- Free keyword research endpoint (`/api/free/search`) now honours both language and country, including localized fallback questions and volume heuristics.
- React/Vite frontend bundles into `static/app`; build with `npm install && npm run build` before packaging a release.
- Flask app factory (`backend.create_app`) is the entry point for Gunicorn and local development; SQLite by default, Postgres via `DATABASE_URL` if provided.
- Deployment automation exists (`deploy.sh`, `auto-deploy.sh`, `quick-deploy.sh`), but the scripts require a quick review before production use (see notes in `DEPLOYMENT-GUIDE.md`).
- Operations runbook covers server sizing, monitoring, and webhook automation—use it alongside the deployment guide.

## Document index

| File | Scope | Notes |
| --- | --- | --- |
| `2025-10-03-privacy-first-locale.md` | Release log for the privacy-first locale update | Tracks Accept-Language behaviour, validation steps, and pending deployment work |
| `DEPLOYMENT-GUIDE.md` | End-to-end droplet deployment playbook | Includes current gaps in the shell scripts and recommended manual steps |
| `DNS-SETUP.md` | Apex DNS + TLS guidance | Root domain only; pair with deployment guide for full launch |
| `localization.md` | Language + SEO implementation | Describes how locale files, Accept-Language, and search params interact |
| `operations.md` | Day-two operations | Runtime config, scaling guidance, monitoring, deploy automation |
| `TODO.md` | Global i18n rollout tracking | Checklist for outstanding localisation tasks |

## Contributing to documentation

- Update the relevant Markdown file(s) alongside the code change; keep prose concise and dated where helpful.
- Run `/usr/local/bin/python3 -m compileall .` after touching backend code referenced in docs, and `npm run build` if instructions rely on the frontend bundle.
- Prefer linking to existing docs inside this folder instead of duplicating instructions.
- If guidance becomes obsolete, either prune it or replace it with a short note capturing the new truth—avoid leaving outdated advice in place.
