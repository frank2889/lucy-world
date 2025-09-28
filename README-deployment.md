# Lucy World Search

Een geavanceerde keyword research tool met gratis en premium functies.

## 🌟 Features

- **Gratis Keyword Research**: Gebruik Google Trends, Wikipedia en andere gratis bronnen
- **Geavanceerde Analytics**: Zoekvolume, moeilijkheidsgraad, CPC en competitie-analyse
- **Multiple Talen**: Ondersteuning voor verschillende talen
- **Export Functionaliteit**: Download resultaten als CSV
- **Moderne UI**: Canva-geïnspireerde interface
- **Real-time Data**: Live keyword trends en suggesties

## 🚀 Deployment op DigitalOcean

### Automatische Deployment

1. **Upload je bestanden** naar je DigitalOcean droplet
2. **Maak het deployment script uitvoerbaar**:
   ```bash
   chmod +x deploy.sh
   ```
3. **Run het deployment script**:
   ```bash
   ./deploy.sh
   ```

### Handmatige Deployment

1. **Maak een Ubuntu 22.04 droplet** op DigitalOcean
2. **Connect via SSH**:
   ```bash
   ssh root@your-droplet-ip
   ```
3. **Clone of upload je project**
4. **Install dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv nginx supervisor
   ```
5. **Setup de applicatie**:
   ```bash
   cd /var/www/
   sudo mkdir lucy-world-search
   sudo chown $USER:$USER lucy-world-search
   # Upload je bestanden hier
   ```
6. **Create virtual environment**:
   ```bash
   cd lucy-world-search
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements-prod.txt
   ```
7. **Configure services** (zie deploy.sh voor details)

### DNS Setup

1. **Ga naar je domain provider** (waar lucy.world is geregistreerd)
2. **Voeg een A record toe**:
   - Name: `search`
   - Type: `A`
   - Value: `YOUR_DROPLET_IP`
   - TTL: `300` (5 minutes)

### SSL Certificate

Het deployment script installeert automatisch een SSL certificaat via Let's Encrypt.

## 📊 Monitoring

### Service Status
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

### Health Check
```bash
curl https://lucy.world/health
```

## 🔄 Updates

Gebruik het update script voor toekomstige updates:
```bash
chmod +x update.sh
./update.sh
```

## 🛠️ Development

### Local Development
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export FLASK_ENV=development
python app.py
```

### Environment Variables
Kopieer `env.example` naar `.env` en pas de waarden aan:
```bash
cp env.example .env
# Edit .env met je eigen waarden
```

## 📁 Project Structure

```
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
└── README.md               # This file
```

## 🌐 Endpoints

### Public Pages
- `/` - Homepage (redirects to free version)
- `/free` - Free keyword research tool
- `/advanced` - Advanced keyword research tool
- `/scale` - Scale page

### API Endpoints
- `POST /api/free/search` - Free keyword search
- `POST /api/advanced/research` - Advanced keyword research
- `POST /api/export/csv` - Export results to CSV
- `GET /health` - Health check

## 🔧 Configuration

### Nginx Configuration
Located at `/etc/nginx/sites-available/lucy-world-search`

### Systemd Service
Located at `/etc/systemd/system/lucy-world-search.service`

### Gunicorn Configuration
See `gunicorn.conf.py`

## 🚨 Troubleshooting

### Application Won't Start
```bash
# Check logs
sudo journalctl -u lucy-world-search -f

# Check if port is in use
sudo netstat -tlnp | grep :8000

# Restart service
sudo systemctl restart lucy-world-search
```

### Nginx Issues
```bash
# Test configuration
sudo nginx -t

# Check status
sudo systemctl status nginx

# Restart nginx
sudo systemctl restart nginx
```

### SSL Certificate Issues
```bash
# Renew certificate
sudo certbot renew

# Check certificate status
sudo certbot status
```

## 📈 Performance

De applicatie is geconfigureerd voor optimale performance:
- **Gunicorn**: 4 workers voor parallelle verwerking
- **Nginx**: Gzip compressie en static file caching
- **SSL**: HTTP/2 ondersteuning
- **Security Headers**: XSS, CSRF en clickjacking bescherming

## 🤝 Support

Voor vragen of problemen, check de logs of neem contact op met het development team.

---

**Live URL**: <https://lucy.world>
