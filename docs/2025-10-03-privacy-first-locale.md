# 2025-10-03 — Privacy-first locale redirect update

## Summary

- Locale detection relies solely on the visitor’s `Accept-Language` header and falls back to `en` without any geo IP inference (commit [`ccd631f`](https://github.com/frank2889/lucy-world/commit/ccd631fba20d0ca3b14d1d5fe3631eb9df2e887)).
- The frontend keeps the UI language stable while letting marketers target any market; the free keyword pipeline now receives the explicit `language`/`country` pair and generates localized follow-up questions through the new language profiles.
- Validation: `python3 -m compileall backend` (syntax check) and `curl https://lucy.world/meta/detect.json -H 'Accept-Language: de'` (verifies server response) both pass locally.
- Deployment via `./quick-deploy.sh` still fails with `Permission denied (publickey)` when connecting to `root@104.248.93.202`, so production is running the pre-update build.

## Next steps

1. Register a deploy key (or import the local SSH key) for `root@104.248.93.202`, or run the deploy from a machine that already has access.
2. Patch `deploy.sh`/Nginx to stop redirecting `/` → `/search`—the SPA now expects language-prefixed paths served from `/`.
3. Re-run the deployment (see `DEPLOYMENT-GUIDE.md`) and spot-check `https://lucy.world/meta/detect.json` with different `Accept-Language` headers afterwards.
4. Smoke test `/api/free/search` for at least two locales (e.g., `lang=de`, `lang=ja`) to confirm the language-aware fallbacks are live.

## Notes

- This change reinforces the “privacy first” promise by eliminating geo inference for locale selection and making the backend’s fallbacks deterministic.
- Frontend work already keeps the UI language sticky; adding a lightweight language switcher remains on the UX backlog (see `TODO.md`).
- Deployment tooling still hardcodes credentials—migrate to SSH keys before enabling unattended runs.
