# Lucy World Search – Deployment Guide (October 2025)

Lucy World Search runs as a Flask application that serves a Vite-built React SPA and exposes `/api/*` endpoints. Locale handling is done on the server—`/` redirects to `/&lt;lang&gt;/` based on `Accept-Language`—so the web server must proxy *all* non-static requests to the Flask app. The steps below describe how to get a droplet ready, ship a new release, and keep deployments repeatable.

> **⚠️ Heads-up:** `deploy.sh` and `quick-deploy.sh` are legacy helpers. They still assume a `/search` homepage and refer to `requirements-prod.txt`, which no longer exists. Treat them as templates and update them before running in production. `auto-deploy.sh` **is maintained** and now powers the automated workflow described below.

## 0. Prerequisites

- **Infrastructure**: Ubuntu 22.04 LTS droplet (1 GB RAM is fine for low traffic) + DNS `A` record pointing `lucy.world` to the droplet (see `DNS-SETUP.md`).
- **Access**: SSH key with root or deploy-user privileges on the droplet. Avoid password auth and update the server’s `sshd_config` accordingly.
- **Local tooling**: Node 20+, npm 10+, Python 3.11+ (project currently uses 3.13), Git, and `zip`/`rsync` if you prefer artifact deployments.
- **Secrets**: Prepare values for `SECRET_KEY`, optional `DATABASE_URL`, SMTP credentials (for magic links), the Search Console service-account variables (`GSC_TYPE`, `GSC_PROJECT_ID`, `GSC_PRIVATE_KEY_ID`, `GSC_PRIVATE_KEY`, `GSC_CLIENT_EMAIL`, `GSC_CLIENT_ID`, `GSC_AUTH_URI`, `GSC_TOKEN_URI`, `GSC_AUTH_PROVIDER_CERT_URL`, `GSC_CLIENT_CERT_URL`, `GSC_UNIVERSE_DOMAIN`), and the Stripe Billing keys: `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_PRICE_PRO`, optional `STRIPE_PRICE_PRO_USAGE`, and `STRIPE_WEBHOOK_SECRET`.

## 1. Prepare a release locally

1. Install frontend dependencies and build the bundle:

    ```bash
    cd frontend
    npm install
    npm run build
    cd ..
    ```

   This writes hashed assets to `static/app`. Commit or copy these files before deploying.
2. Still in `frontend/`, run the Vitest suite to confirm the entitlement store and guards load correctly:

    ```bash
    npm test
    ```

   The tests cover the `useEntitlements` hook, context provider, and `RequireEntitlement` guard added on Oct 5 2025.
3. Regenerate locale SEO assets and validate crawl discipline (this also rewrites every `languages/*/robots.txt` with the latest `Disallow: /*?q=` rule):

    ```bash
    python3 scripts/generate_site_assets.py
    python3 scripts/validate_robots.py
    ```

   The validator fails if any locale is missing the query-string disallow, sitemap pointer, or hreflang permissions.
4. Run a quick syntax check on the backend:

    ```bash
    /usr/local/bin/python3 -m compileall backend free_keyword_tool.py advanced_keyword_tool.py
    ```

5. (Optional) Spin up the lightweight `.pytest-venv` and run the crawl/indexing regression suite before shipping:

    ```bash
    python3 -m venv .pytest-venv
    .pytest-venv/bin/pip install -r requirements.txt pytest markdown stripe
    .pytest-venv/bin/python -m pytest backend/tests/test_indexing.py backend/tests/test_entitlements.py
    ```

   This confirms search-result pages emit `noindex, nofollow` and the entitlements API keeps expiry metadata stable.
6. (Optional) Create a git tag or archive for the release so you can trace what is live.

## 2. Ship code to the server

**Preferred:** push to GitHub (or your chosen remote) and pull on the server. The webhook service (`webhook.py`) is built for this flow.

```bash
git add .
git commit -m "Deploy: privacy-first locale rollout"
git push origin main
```

**Alternative:** package and copy manually.

```bash
zip -r lucy-world-search.zip . -x "*.pyc" ".venv/*" "node_modules/*"
scp lucy-world-search.zip root@<droplet_ip>:/var/www/
```

## 3. Bootstrap the droplet (first run)

```bash
ssh root@<droplet_ip>
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip nginx git

mkdir -p /var/www/lucy-world-search
cd /var/www/lucy-world-search
git clone https://github.com/frank2889/lucy-world.git .  # or extract the uploaded zip

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Copy the built frontend bundle if you built locally
# (skip if you run `npm run build` on the server)

cat > .env <<'EOF'
FLASK_ENV=production
SECRET_KEY=<generate_with_python>
PUBLIC_BASE_URL=https://lucy.world
# Search Console service account (escape newlines with \n)
GSC_TYPE=service_account
GSC_PROJECT_ID=<your_project_id>
GSC_PRIVATE_KEY_ID=<your_private_key_id>
GSC_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
GSC_CLIENT_EMAIL=<service-account@your-project.iam.gserviceaccount.com>
GSC_CLIENT_ID=<service_account_client_id>
GSC_AUTH_URI=https://accounts.google.com/o/oauth2/auth
GSC_TOKEN_URI=https://oauth2.googleapis.com/token
GSC_AUTH_PROVIDER_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
GSC_CLIENT_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/<urlencoded_service_account>
GSC_UNIVERSE_DOMAIN=googleapis.com

# Stripe Billing (Checkout + customer portal)
STRIPE_PUBLISHABLE_KEY=<stripe_publishable_key>
STRIPE_SECRET_KEY=<stripe_secret_key>
STRIPE_PRICE_PRO=<stripe_price_id>
# Optional usage-based add-on price
STRIPE_PRICE_PRO_USAGE=<optional_usage_price_id>
STRIPE_WEBHOOK_SECRET=<stripe_webhook_secret>

# DATABASE_URL=postgresql://...
# SMTP_HOST=...
# SMTP_PORT=587
# SMTP_USERNAME=...
# SMTP_PASSWORD=...
# SMTP_FROM=no-reply@lucy.world
EOF

# Align the legacy SQLite schema with the current app model
python3 scripts/migrate_add_user_plan_columns.py --db lucy.sqlite3

# Inspect the results (optional dry run)
# python3 scripts/migrate_add_user_plan_columns.py --db lucy.sqlite3 --dry-run

# Confirm the required columns exist
sqlite3 lucy.sqlite3 "PRAGMA table_info(users);"
```

### Systemd service

Create `/etc/systemd/system/lucy-world-search.service`:

```ini
[Unit]
Description=Lucy World Search
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/lucy-world-search
Environment="PATH=/var/www/lucy-world-search/venv/bin"
EnvironmentFile=/var/www/lucy-world-search/.env
ExecStart=/var/www/lucy-world-search/venv/bin/gunicorn --config gunicorn.conf.py wsgi:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable lucy-world-search
sudo systemctl start lucy-world-search
```

### Nginx reverse proxy

Replace `/etc/nginx/sites-available/lucy-world-search` with:

```nginx
server {
    listen 80;
    server_name lucy.world;

    # Redirect HTTP → HTTPS once TLS is in place
    if ($host = lucy.world) {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name lucy.world;

    ssl_certificate /etc/letsencrypt/live/lucy.world/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/lucy.world/privkey.pem;

    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header Referrer-Policy strict-origin-when-cross-origin;

    gzip on;
    gzip_types text/plain text/css application/json application/javascript;

    root /var/www/lucy-world-search/static;

    location /static/ {
        alias /var/www/lucy-world-search/static/;
        try_files $uri =404;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /app/ {
        alias /var/www/lucy-world-search/static/app/;
        try_files $uri =404;
        expires 1w;
    }

    location / {
        try_files $uri @flask;
    }

    location @flask {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }
}
```

Enable the site, request a certificate, and reload:

```bash
sudo ln -sf /etc/nginx/sites-available/lucy-world-search /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d lucy.world --email frank@lucy.world --agree-tos --non-interactive
```

## 4. Verification checklist

```bash
systemctl status lucy-world-search
curl -I https://lucy.world
curl -s https://lucy.world/meta/detect.json -H 'Accept-Language: fr'
curl -s https://lucy.world/api/free/search -X POST -H 'Content-Type: application/json' \
  -d '{"keyword":"marketing","language":"fr","country":"FR"}' | jq '.language'
```

Confirm that `language` in the response matches the request, and that `trends.trend_direction` is present. Visit `https://lucy.world/` in a browser with Dutch and German `Accept-Language` headers to ensure the redirect and UI strings behave as expected.

### Ongoing health monitoring

Keep the Gunicorn service honest with the repository's probe helper:

```bash
python3 scripts/monitor_gunicorn_service.py --base-url https://lucy.world --service lucy-world-search
```

Schedule it via cron or a systemd timer to alert if the HTTP checks or the systemd unit fall over.

To keep an eye on hreflang health and Search Console coverage, run the GSC monitor once OAuth access is configured:

```bash
python3 scripts/gsc_monitor.py --site https://lucy.world/ --lookback 14
```

## 5. Automating deployments

### GitHub Actions workflow (preferred)

A first-class GitHub Actions workflow (`.github/workflows/deploy.yml`) now ships every push to `main`:

1. **Provision SSH access** dedicated to CI. Create a deploy user on the droplet with read/write access to `/var/www/lucy-world-search`, install the GitHub Action public key, and confirm passwordless SSH.
2. **Set repository secrets** (`Settings → Secrets and variables → Actions`):
   - `DEPLOY_HOST`: droplet IP or hostname.
   - `DEPLOY_USER`: deploy username (for example, `deploy`).
   - `DEPLOY_KEY`: private key that matches the server’s authorized key.
   - Optional overrides: `DEPLOY_PORT`, `DEPLOY_APP_DIR`, `DEPLOY_REPO_URL`, `DEPLOY_HEALTH_URL`, `DEPLOY_SERVICE_NAME`, `DEPLOY_NGINX_SERVICE`, `DEPLOY_VENV_PATH`, `DEPLOY_REQUIREMENTS_FILE`.
3. **Verify server prerequisites**: the droplet must already contain the repo at `/var/www/lucy-world-search` (or your override), a working virtual environment, and the refreshed `auto-deploy.sh`. Run once:

    ```bash
    cd /var/www/lucy-world-search
    sudo install -m 755 auto-deploy.sh /usr/local/bin/auto-deploy-lucy
    ```

    The workflow calls `auto-deploy.sh` remotely, so it must remain up to date in the repository and on the server.
4. **Trigger a deployment**. Push to `main` or click “Run workflow” in GitHub. The Action connects over SSH, exports the supplied environment variables, and executes `auto-deploy.sh`, which pulls the latest commit, installs dependencies from `requirements.txt`, optionally builds the frontend, restarts `systemd` services, and performs a health check.

Deployment logs appear in the Actions run and the server journal (`journalctl -u lucy-world-search`).

### Webhook fallback (legacy)

If you prefer to keep the self-hosted webhook (`webhook.py`), reuse steps 1–2 above, then:

1. Create `/etc/systemd/system/lucy-webhook.service` as shown previously, enable it, and ensure the process listens on port `9000`.
2. Add a GitHub webhook pointing to `https://lucy.world:9000/webhook` with the shared secret. The webhook also invokes `auto-deploy.sh` whenever it receives a push event.

See `operations.md` for operational monitoring and scheduled maintenance once automation is live.

## 6. TLS renewals

TLS certificates are handled by Certbot. The repository includes `scripts/renew_tls.sh` to run `certbot renew`, reload Nginx, and refresh the Gunicorn unit once new certificates are issued.

1. Copy the script to `/usr/local/bin/renew-lucy-tls` and make it executable:

    ```bash
    sudo install -m 755 scripts/renew_tls.sh /usr/local/bin/renew-lucy-tls
    ```

2. Test the workflow with a dry run:

    ```bash
    sudo CERTBOT_BIN=/usr/bin/certbot /usr/local/bin/renew-lucy-tls --domain lucy.world --dry-run
    ```

3. When the dry run succeeds, create `/etc/systemd/system/renew-lucy-tls.timer` to run the script twice a day:

    ```ini
    [Unit]
    Description=Renew Lucy.world TLS certificates

    [Timer]
    OnCalendar=*-*-* 02:00:00
    OnCalendar=*-*-* 14:00:00
    Persistent=true

    [Install]
    WantedBy=timers.target
    ```

    ```bash
    sudo systemctl enable --now renew-lucy-tls.timer
    ```

The timer ensures certificates renew automatically and Nginx/Gunicorn pick up the new chain without manual intervention.

## 7. Localization workflow

Keeping the UI strings in sync is now a two-step process. Run these checks locally before opening a pull request, and they also execute in CI:

1. **Audit translator coverage.** From the repo root run:

    ```bash
    /usr/local/bin/python3 scripts/validate_locale_keys.py --strict
    ```

    This enumerates every translator key in the frontend bundle and asserts the key exists in every `languages/<locale>/locale.json`. The script exits non-zero on missing keys and lists the offending locale(s). Avoid dynamic translator calls (for example, ``translate(`platform.${id}.description`)``) so the auditor can detect the string at build time.

2. **Backfill missing entries.** If keys are missing, copy the English string into the target locale while waiting for real translations:

    ```bash
    /usr/local/bin/python3 scripts/backfill_locale_keys.py --source en --locales fr de es
    ```

    The script preserves existing translations and writes sorted JSON for readability. Always commit the updated locale files after a backfill.

3. **Regenerate and validate assets.** Re-run `python scripts/generate_site_assets.py --all` followed by `python scripts/validate_enhanced_locales.py --strict` if you change sitemap or hreflang metadata; CI relies on the same commands.

## 7. Known gaps / TODOs

- Update `deploy.sh` and `quick-deploy.sh` to reference `requirements.txt`, respect the new locale-aware routing, and drop the password-based SSH usage in `quick-deploy.sh`.
- Consider creating a dedicated deploy user with limited permissions instead of running everything as `root`/`www-data`.
- Add health probes for `/meta/detect.json` and `/api/free/search` to DigitalOcean monitoring once production is cut over.
- Document rollback steps (e.g., keep the previous git commit hash handy and restart the service after `git checkout`).
