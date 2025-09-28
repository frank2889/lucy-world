# 🚀 Lucy World Search – DigitalOcean Deployment Guide

## Stap 1: DigitalOcean Droplet Setup

1. **Maak een nieuwe Droplet**

   - Ga naar DigitalOcean Dashboard
   - Klik "Create" → "Droplets"
   - Kies **Ubuntu 22.04 LTS**
   - Selecteer **Basic Plan** ($6/maand - 1GB RAM, 1 vCPU, 25GB SSD)
   - Kies **Amsterdam datacenter** (voor Nederlandse gebruikers)
   - Voeg je **SSH Key** toe
   - Hostname: `lucy-world-search`

2. **Noteer het IP-adres** van je droplet

## Stap 2: DNS Configuratie (root domein)

1. **Ga naar je domain provider** (waar lucy.world geregistreerd is)
2. **Voeg een A-record toe voor het hoofddomein (root)**

   ```text
   Name: @ (root)
   Type: A
   Value: [JE_DROPLET_IP_ADRES]
   TTL: 300
   ```

3. **Wacht 5-10 minuten** voor DNS propagatie

## Stap 3: Bestanden Uploaden

### Optie A – Met SCP (Aanbevolen)

```bash
# Pak alle bestanden in een zip
cd "/Users/Frank/Library/Mobile Documents/com~apple~CloudDocs/visualstudio/lucy world search"
zip -r lucy-world-search.zip . -x "*.pyc" "__pycache__/*" ".venv/*"

# Upload naar server
scp lucy-world-search.zip root@[JE_DROPLET_IP]:/tmp/
```

### Optie B – Met Git

```bash
# Op je lokale machine
git init
git add .
git commit -m "Initial deployment"
git remote add origin [JE_GIT_REPO_URL]
git push -u origin main

# Op de server
git clone [JE_GIT_REPO_URL] /var/www/lucy-world-search
```

## Stap 4: Server Setup

1. **SSH naar je server**:

   ```bash
   ssh root@[JE_DROPLET_IP]
   ```

2. **Extract bestanden** (als je SCP gebruikt hebt):

   ```bash
   cd /var/www
   unzip /tmp/lucy-world-search.zip -d lucy-world-search
   cd lucy-world-search
   ```

3. **Run het deployment script**:

   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

## Stap 5: Controleer of alles werkt

1. **Check service status**:

   ```bash
   sudo systemctl status lucy-world-search
   sudo systemctl status nginx
   ```

2. **Test de website**:

   ```bash
   curl http://lucy.world/health
   ```

3. **Open in browser**:
   - Http: `http://lucy.world`
   - Https: `https://lucy.world` (na SSL setup)

## Stap 6: SSL Certificaat (Automatisch)

Het deployment script installeert automatisch een SSL certificaat via Let's Encrypt.

Als dit niet werkt, run handmatig:

```bash
sudo certbot --nginx -d lucy.world --email frank@lucy.world --agree-tos --non-interactive
```

## 🔧 Handige Commando's

### Service Management

```bash
# Restart applicatie
sudo systemctl restart lucy-world-search

# Check logs
sudo journalctl -u lucy-world-search -f

# Check nginx logs
sudo tail -f /var/log/nginx/access.log
```

### Updates

```bash
# Upload nieuwe bestanden en run:
./update.sh
```

### Monitoring

```bash
# CPU en memory gebruik
htop

# Disk usage
df -h

# Check welke poorten open zijn
sudo netstat -tlnp
```

## 📊 Expected Results

Na succesvolle deployment heb je:

✅ **Live website**: <https://lucy.world>  
✅ **SSL certificaat**: Automatisch via Let's Encrypt  
✅ **Nginx reverse proxy**: Voor performance en security  
✅ **Systemd service**: Automatische restart bij crashes  
✅ **Health monitoring**: `/health` endpoint  
✅ **Log management**: Centralized logging  

## 🚨 Troubleshooting

### Website niet bereikbaar

1. Check DNS: `nslookup lucy.world`
2. Check nginx: `sudo systemctl status nginx`
3. Check app: `sudo systemctl status lucy-world-search`

### Performance monitoring (1GB RAM server)

```bash
# Basic resource monitoring
htop                    # CPU en RAM usage
free -h                 # Memory usage
df -h                   # Disk usage
sudo netstat -tlnp      # Active connections
```

### SSL problemen

```bash
sudo certbot renew --dry-run
sudo nginx -t
sudo systemctl restart nginx
```

### Performance problemen

```bash
# Check resource usage
htop
iostat 1
```

### Application errors

```bash
# Detailed logs
sudo journalctl -u lucy-world-search -f --no-pager
```

## 💡 Tips

1. **Monitor resources**: Een $6 droplet heeft 1GB RAM - perfect voor deze applicatie
2. **Backup**: Maak regelmatig DigitalOcean snapshots
3. **Updates**: Gebruik altijd het `update.sh` script
4. **Security**: Verander standaard SSH poort en gebruik fail2ban
5. **Monitoring**: Setup DigitalOcean monitoring voor alerts

## 🎯 Next Steps

Na deployment kun je:

- **Google Analytics** toevoegen voor usage tracking
- **API rate limiting** implementeren
- **Caching** toevoegen met Redis
- **Database** toevoegen voor user management
- **CDN** setup voor static files

---

**Success!** Je Lucy World Search tool is nu live op <https://lucy.world> 🎉
