# Lucy World Search — Deployment (DigitalOcean)

Deze gids beschrijft een schone en bewezen manier om Lucy World Search te deployen op een DigitalOcean droplet met het apex/root domein lucy.world.

## 🌟 Features (overzicht)

- Gratis en geavanceerde keyword research
- Multi-language UI, moderne interface, CSV export
- Health endpoint, logs, SSL met Let's Encrypt

## 🚀 Snelle automatische deployment

1. Upload je bestanden naar je DigitalOcean droplet
2. Maak het deployment script uitvoerbaar:

   ```bash
   chmod +x deploy.sh
   ```

3. Start de deployment:

   ```bash
   ./deploy.sh
   ```

## 🧰 Handmatige deployment (alternatief)

1. Maak een Ubuntu 22.04 droplet op DigitalOcean
2. Verbind via SSH:

   ```bash
   ssh root@YOUR_DROPLET_IP
   ```

3. Upload of clone het project
4. Installeer dependencies:

   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip python3-venv nginx supervisor
   ```

5. Maak de projectmap en zet bestanden klaar:

   ```bash
   mkdir -p /var/www/lucy-world-search
   cd /var/www/lucy-world-search
   # Upload of clone hier de bestanden
   ```

6. Maak en activeer een virtualenv en installeer Python dependencies:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements-prod.txt
   ```

7. Configureer services (zie deploy.sh voor details) en start de app

## 🌐 DNS setup (apex/root domein)

Voeg bij je domain provider een A-record toe voor lucy.world:

- Name: @ (root)
- Type: A
- Value: YOUR_DROPLET_IP
- TTL: 300

## 🔒 SSL certificaat

Het deployment script zet automatisch een certificaat via Let's Encrypt. Als fallback kun je handmatig uitvoeren:

```bash
sudo certbot --nginx -d lucy.world --email frank@lucy.world --agree-tos --non-interactive
```

## 📊 Monitoring en health

### Service status

```bash
sudo systemctl status lucy-world-search
sudo systemctl status nginx
```

### Logs

```bash
# Application logs
sudo journalctl -u lucy-world-search -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Health check

```bash
curl https://lucy.world/health
```

## 🔄 Updates

Gebruik het update script voor toekomstige updates:

```bash
chmod +x update.sh
./update.sh
```

## 🛠️ Development (lokaal)

### Project starten

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export FLASK_ENV=development
python app.py
```

### Environment variables

```bash
cp env.example .env
# Pas .env aan met je eigen waarden
```

## 📁 Projectstructuur (beknopt)

```text
lucy-world-search/
├── app.py                    # Main production app
├── web_app.py               # Advanced keyword research
├── free_web_app.py          # Free keyword research
├── advanced_keyword_tool.py # Advanced keyword logic
├── free_keyword_tool.py     # Free keyword logic
├── templates/               # HTML templates
├── static/                  # CSS, JS, images
├── requirements-prod.txt    # Production dependencies
├── gunicorn.conf.py        # Gunicorn configuration
├── deploy.sh               # Deployment script
├── update.sh               # Update script
└── README.md               # Readme
```

## 🌐 Publieke pagina’s en API

### Pagina’s

- `/` – Homepage (redirect naar free)
- `/free` – Free keyword research tool
- `/advanced` – Advanced keyword research tool
- `/scale` – Scale page

### API endpoints

- `POST /api/free/search` – Free keyword search
- `POST /api/advanced/research` – Advanced keyword research
- `POST /api/export/csv` – Export results naar CSV
- `GET /health` – Health check

## 🔧 Configuratie

- Nginx: `/etc/nginx/sites-available/lucy-world-search`
- Systemd: `/etc/systemd/system/lucy-world-search.service`
- Gunicorn: `gunicorn.conf.py`

## 🚨 Troubleshooting

### App start niet

```bash
# Logs
sudo journalctl -u lucy-world-search -f

# Poort in gebruik?
sudo netstat -tlnp | grep :8000

# Herstart
sudo systemctl restart lucy-world-search
```

### Nginx issues

```bash
sudo nginx -t
sudo systemctl status nginx
sudo systemctl restart nginx
```

### SSL issues

```bash
sudo certbot renew --dry-run
sudo certbot renew
```

## 📈 Performance (basis)

-
- Gunicorn: 4 workers voor parallelle requests
- Nginx: Gzip + caching voor statische assets
- SSL: HTTP/2 ingeschakeld

## ✅ Live

Hoofdsite: <https://lucy.world>

## 🤝 Support

Voor vragen of problemen, check de logs of neem contact op met het development team.
