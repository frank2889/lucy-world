# 🌐 DNS setup voor lucy.world (October 2025)

> Only the apex domain (`lucy.world`) is currently routed. Configure `www` when the web server has a redirect in place, otherwise keep DNS minimal to avoid stray traffic.

## 1. Controleer het droplet IP

```bash
# SSH naar je server en noteer het publieke IP
ssh root@YOUR_DROPLET_IP
curl -4 icanhazip.com
```

## 2. Configureer de apex-record

1. Log in bij je domain provider (Cloudflare, Namecheap, GoDaddy, …).
2. Open het DNS-beheer voor `lucy.world`.
3. Voeg of update het A-record voor het hoofddomein:

```text
Type: A
Name: @
Value: <DROPLET_IP>
TTL: 300
```

### Option eel: www redirect voorbereiden

Add the CNAME only if Nginx already redirects `www` → apex:

```text
Type: CNAME
Name: www
Value: lucy.world
TTL: 300
```

## 3. Test DNS propagatie

```bash
nslookup lucy.world
dig lucy.world @8.8.8.8
dig lucy.world @1.1.1.1
```

Use <https://www.whatsmydns.net/> for a visual check if needed.

## 4. Vraag het TLS-certificaat aan

```bash
ssh root@YOUR_DROPLET_IP
sudo apt update
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d lucy.world --email frank@lucy.world --agree-tos --non-interactive
sudo certbot renew --dry-run
```

> Verify the systemd timer afterwards: `systemctl list-timers | grep certbot`. Certificates expire every 90 days.

## 5. Controleer (of maak) de Nginx-config

Certbot updates the TLS bits but does not build app routes. Ensure `/etc/nginx/sites-available/lucy-world-search` contains something equivalent to:

```nginx
server {
    listen 80;
    server_name lucy.world;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name lucy.world;

    ssl_certificate /etc/letsencrypt/live/lucy.world/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/lucy.world/privkey.pem;

    root /var/www/lucy-world-search/static;

    location /static/ {
        alias /var/www/lucy-world-search/static/;
        try_files $uri =404;
        expires 1y;
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
    }

```

Reload Nginx and check the syntax:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 6. Run snelle checks

```bash
curl -I http://lucy.world            # Verwacht 301 naar HTTPS
curl -I https://lucy.world
curl -s https://lucy.world/health
```

## Troubleshooting snippets

- **DNS werkt niet**:

    ```bash
    dig lucy.world
    dig lucy.world @1.1.1.1
    ```

- **SSL issues**:

    ```bash
    sudo certbot certificates
    sudo certbot renew --force-renewal -d lucy.world
    sudo nginx -t
    ```

- **Site down**:

    ```bash
    sudo systemctl status lucy-world-search
    sudo systemctl status nginx
    sudo journalctl -u lucy-world-search -f
    ```

## Checklist

- [ ] Apex A-record published
- [ ] `nslookup lucy.world` resolves to droplet IP
- [ ] Certbot certificate issued and renewal tested
- [ ] HTTP → HTTPS redirect confirmed
- [ ] `/health` responds over HTTPS
