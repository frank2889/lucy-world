# Lucy World Docs

This folder is the single source of truth for all Markdown documentation. When you add or update docs, place the `.md` file here (or within a subfolder of `docs/`) rather than at the project root, so future contributors know where to look.

Contents:

- DEPLOYMENT-GUIDE.md — DigitalOcean deployment steps
- DNS-SETUP.md — DNS instructions (apex domain, www/redirects)
- GITHUB-WORKFLOW.md — CI/CD via GitHub Actions
- LAUNCH-SUMMARY.md — overview and launch checklist
- PRODUCTION-CONFIG.md — environment variables and config
- SCALING-GUIDE.md — scaling and performance tips

## Frontend copy & localization rule

- Never hard-code interface text in a single language inside the frontend source.
- Expose new strings through the localization system (`languages/<lang>/locale.json` and `/meta/locales.json`) with a neutral default value.
- For React components, reference UI text via the `ui?.strings` map (with a sensible fallback) so translators can provide localized values without touching the component logic.
