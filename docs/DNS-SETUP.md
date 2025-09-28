# 🌐 DNS Setup voor lucy.world (root domein)

## Stap 1: Controleer je Droplet IP
```bash
# SSH naar je server
ssh root@YOUR_DROPLET_IP

# Check het externe IP adres
curl -4 icanhazip.com
```

## Stap 2: DNS Configuratie

### Bij je Domain Provider (waar lucy.world geregistreerd is):

1. **Login** bij je domain provider (Namecheap, GoDaddy, Cloudflare, etc.)
2. **Ga naar DNS Management** voor lucy.world
3. **Update/Voeg A Record toe voor hoofddomain**:

```
Type: A
Name: @ (or leave empty for root domain)
Value: [JE_DROPLET_IP_ADRES] 
TTL: 300 (5 minutes)
```

### Voorbeeld configuraties (root / apex)

#### Cloudflare:
```
Type: A
Name: @
IPv4 Address: YOUR_DROPLET_IP
Proxy Status: DNS only (grey cloud)
TTL: Auto
```

#### Namecheap:
```
Type: A Record
Host: @
Value: YOUR_DROPLET_IP
TTL: 5 min
```

#### GoDaddy:
```
Type: A
Name: @
Value: YOUR_DROPLET_IP
TTL: 600 seconds
```

## Stap 3: Test DNS Propagation

```bash
# Test vanaf je lokale machine
nslookup lucy.world

# Test vanaf verschillende locaties
dig lucy.world @8.8.8.8
dig lucy.world @1.1.1.1

# Online DNS checker
# Ga naar: https://www.whatsmydns.net/
# Enter: lucy.world
```

## Stap 4: SSL Certificaat Setup

```bash
# SSH naar je server
ssh root@YOUR_DROPLET_IP

# Install Certbot (als nog niet gedaan)
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# Krijg SSL certificaat
sudo certbot --nginx -d lucy.world --email frank@lucy.world --agree-tos --non-interactive

# Test automatische renewal
sudo certbot renew --dry-run
```

## Stap 5: Update Nginx Configuratie

Je nginx configuratie zou automatisch geüpdatet moeten zijn door certbot, maar check het:

```bash
sudo nano /etc/nginx/sites-available/lucy-world-search
```

Het zou er zo uit moeten zien:
```nginx
server {
	server_name lucy.world;
    
	location / {
		proxy_pass http://127.0.0.1:8000;
		proxy_set_header Host $host;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header X-Forwarded-Proto $scheme;
	}
    
	location /static {
		alias /var/www/lucy-world-search/static;
		expires 1y;
	}

	listen 443 ssl; # managed by Certbot
	ssl_certificate /etc/letsencrypt/live/lucy.world/fullchain.pem;
	ssl_certificate_key /etc/letsencrypt/live/lucy.world/privkey.pem;
	include /etc/letsencrypt/options-ssl-nginx.conf;
	ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

server {
	if ($host = lucy.world) {
		return 301 https://$host$request_uri;
	}

	listen 80;
	server_name lucy.world;
	return 404;
}
```

## Stap 6: Test de Website

```bash
# Test HTTP redirect naar HTTPS
curl -I http://lucy.world

# Test HTTPS
curl -I https://lucy.world

# Test health endpoint
curl https://lucy.world/health
```

## 🚨 Troubleshooting

### DNS werkt niet:
```bash
# Check of de A record bestaat
dig lucy.world

# Check vanaf verschillende DNS servers
dig lucy.world @8.8.8.8
dig lucy.world @1.1.1.1
```

### SSL certificaat problemen:
```bash
# Check certificate status
sudo certbot certificates

# Force renewal
sudo certbot renew --force-renewal -d lucy.world

# Check nginx syntax
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

### Website niet bereikbaar:
```bash
# Check services
sudo systemctl status lucy-world-search
sudo systemctl status nginx

# Check logs
sudo journalctl -u lucy-world-search -f
sudo tail -f /var/log/nginx/error.log
```

## ⏱️ Timeline

- **DNS Setup**: 2-5 minuten
- **DNS Propagation**: 5-30 minuten (wereldwijd)
- **SSL Certificate**: 1-2 minuten
- **Total**: 10-40 minuten tot volledig werkend

## ✅ Success Checklist

- [ ] A Record toegevoegd bij domain provider
- [ ] DNS propagation check: `nslookup lucy.world`
- [ ] SSL certificaat geïnstalleerd
- [ ] HTTPS redirect werkt
- [ ] Website bereikbaar op <https://lucy.world>
- [ ] Health check werkt: <https://lucy.world/health>

---

Na deze stappen is lucy.world live! 🎉
