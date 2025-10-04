# Lucy World Search – Deployment Guide (October 2025)

Lucy World Search runs as a Flask application that serves a Vite-built React SPA and exposes `/api/*` endpoints. Locale handling is done on the server—`/` redirects to `/&lt;lang&gt;/` based on `Accept-Language`—so the web server must proxy *all* non-static requests to the Flask app. The steps below describe how to get a droplet ready, ship a new release, and keep deployments repeatable.

> **⚠️ Heads-up:** `deploy.sh`, `auto-deploy.sh`, and `quick-deploy.sh` are legacy helpers. They still assume a `/search` homepage and refer to `requirements-prod.txt`, which no longer exists. Treat them as templates and update them before running in production.

## 0. Prerequisites

- **Infrastructure**: Ubuntu 22.04 LTS droplet (1 GB RAM is fine for low traffic) + DNS `A` record pointing `lucy.world` to the droplet (see `DNS-SETUP.md`).
- **Access**: SSH key with root or deploy-user privileges on the droplet. Avoid password auth and update the server’s `sshd_config` accordingly.
- **Local tooling**: Node 20+, npm 10+, Python 3.11+ (project currently uses 3.13), Git, and `zip`/`rsync` if you prefer artifact deployments.
- **Secrets**: Prepare values for `SECRET_KEY`, optional `DATABASE_URL`, and SMTP credentials if email sign-in needs to work.

## 1. Prepare a release locally

1. Install frontend dependencies and build the bundle:

    ```bash
    cd frontend
    npm install
    npm run build
    cd ..
    ```

   This writes hashed assets to `static/app`. Commit or copy these files before deploying.
2. Run a quick syntax check on the backend:

    ```bash
    /usr/local/bin/python3 -m compileall backend free_keyword_tool.py advanced_keyword_tool.py
    ```

3. (Optional) Create a git tag or archive for the release so you can trace what is live.

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
# DATABASE_URL=postgresql://...
# SMTP_HOST=...
# SMTP_PORT=587
# SMTP_USERNAME=...
# SMTP_PASSWORD=...
# SMTP_FROM=no-reply@lucy.world
EOF
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

## 5. Automating deployments

Automation keeps production in sync with `main` after each push:

1. **Attach the Git remote** on the droplet (once):

    ```bash
    cd /var/www/lucy-world-search
    git remote set-url origin https://github.com/frank2889/lucy-world.git
    git fetch origin
    git reset --hard origin/main
    ```

2. **Refresh the helper scripts**: update `deploy.sh`, `auto-deploy.sh`, and `quick-deploy.sh` to reference `requirements.txt`, drop hard-coded passwords, and call `systemctl restart lucy-world-search` at the end. Install the reviewed `auto-deploy.sh` to `/usr/local/bin/`:

    ```bash
    sudo install -m 755 auto-deploy.sh /usr/local/bin/auto-deploy-lucy
    ```

3. **Configure the webhook service**. Create `/etc/systemd/system/lucy-webhook.service`:

    ```ini
    [Unit]
    Description=Lucy World Deploy Webhook
    After=network.target

    [Service]
    WorkingDirectory=/var/www/lucy-world-search
    Environment="WEBHOOK_SECRET=<set-this>"
    ExecStart=/var/www/lucy-world-search/venv/bin/python webhook.py
    Restart=on-failure

    [Install]
    WantedBy=multi-user.target
    ```

    Enable it with `sudo systemctl enable --now lucy-webhook`.

4. **Add the GitHub webhook** (repo → Settings → Webhooks): URL `https://lucy.world:9000/webhook`, content type `application/json`, secret matching the environment variable, events = push. Verify with the “Recent Deliveries” tab.

5. **Developer loop**: `git add`, `git commit`, `git push origin main`. The webhook runs `auto-deploy.sh`, pulls the new commit, reinstalls dependencies when needed, and restarts the Gunicorn service. Keep smoke-test commands in pull requests so deploy logs show what was validated upstream.

See `operations.md` for operational monitoring and scheduled maintenance once automation is live.

## 6. Known gaps / TODOs

- Update `deploy.sh` and `auto-deploy.sh` to reference `requirements.txt`, respect the new locale-aware routing, and drop the password-based SSH usage in `quick-deploy.sh`.
- Consider creating a dedicated deploy user with limited permissions instead of running everything as `root`/`www-data`.
- Add health probes for `/meta/detect.json` and `/api/free/search` to DigitalOcean monitoring once production is cut over.
- Document rollback steps (e.g., keep the previous git commit hash handy and restart the service after `git checkout`).
