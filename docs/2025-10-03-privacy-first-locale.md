# 2025-10-03 — Privacy-first locale redirect update

## Summary

- Locale detection now respects only the visitor’s `Accept-Language` header and otherwise defaults to English. Geo-based fallbacks were removed in commit [`ccd631f`](https://github.com/frank2889/lucy-world/commit/ccd631fba20d0ca3b14d1d5fe3631eb9df2e887).
- Verified locally with `python3 -m compileall backend` and via `curl https://lucy.world/meta/detect.json` using custom `Accept-Language` headers.
- Deployment script (`./quick-deploy.sh`) failed: `Permission denied (publickey)` while connecting to `root@104.248.93.202`, so production still serves the previous build.

## Next steps

1. Authorize the correct SSH key on the deployment target (or run the deploy from an environment with existing access).
2. Re-run `./quick-deploy.sh` to publish the change.
3. After deployment, spot-check `https://lucy.world/meta/detect.json` with different `Accept-Language` headers to confirm the live behavior.

## Notes

- This change reinforces the "privacy first" promise by eliminating geo inference for locale selection.
- Consider adding an in-app language switcher so visitors can manually override the detected language if needed.
