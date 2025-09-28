# 🔄 Lucy World Search – Scaling Guide

## Start met $6/maand – Schaal op wanneer nodig

### 📊 Huidige Setup ($6/maand)

- **1GB RAM, 1 vCPU, 25GB SSD**
- **2 Gunicorn workers**
- **Perfect voor:** Testing, ontwikkeling, eerste gebruikers
- **Capaciteit:** 50-100 dagelijkse gebruikers

## 🚀 Upgrade Triggers

### Wanneer upgraden naar $12/maand (2GB RAM)

- **CPU usage** constant >80%
- **RAM usage** constant >85%
- **Response times** >5 seconden
- **500+ daily active users**

```bash
# Check huidige usage
htop
free -h
sudo systemctl status lucy-world-search
```

### Wanneer upgraden naar $24/maand (4GB RAM)

- **1000+ daily users**
- **Multiple concurrent searches** vertragen
- **Need voor caching** (Redis)

## 🔧 Upgrade Process

### Stap 1: DigitalOcean Resize

1. **DigitalOcean Dashboard** → je droplet
2. **Resize** → Kies nieuwe grootte
3. **Power off** droplet voor resize
4. **Power on** na resize

### Stap 2: Update Gunicorn Config

```bash
# SSH naar je server
ssh root@lucy.world

# Edit Gunicorn config
sudo nano /var/www/lucy-world-search/gunicorn.conf.py
```

### Stap 3: Restart Services

```bash
sudo systemctl restart lucy-world-search
sudo systemctl restart nginx
```

## 📈 Upgrade Configurations

### $12/maand (2GB RAM, 1 vCPU)

```python
# gunicorn.conf.py changes
workers = 3  # More workers with more RAM
worker_connections = 750
max_requests = 1500
```

**Capaciteit:** 100-200 daily users

### $24/maand (4GB RAM, 2 vCPUs)

```python
# gunicorn.conf.py changes
workers = 4  # Match CPU cores
worker_connections = 1000
max_requests = 2000
timeout = 45
```

**Capaciteit:** 200-500 daily users

### $48/maand (8GB RAM, 4 vCPUs)

```python
# gunicorn.conf.py changes
workers = 8  # 2x CPU cores
worker_connections = 2000
max_requests = 3000
timeout = 60
```

**Capaciteit:** 500-1000 daily users

## 🎯 Monitoring & Alerts

### Set up monitoring om te weten wanneer te upgraden

```bash
# Simple monitoring script
cat > /usr/local/bin/server-monitor.sh << 'EOF'
#!/bin/bash
CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
RAM=$(free | grep Mem | awk '{printf("%.2f", $3/$2 * 100.0)}')

if (( $(echo "$CPU > 80" | bc -l) )); then
  echo "High CPU: $CPU%" | mail -s "Server Alert" frank@lucy.world
fi

if (( $(echo "$RAM > 85" | bc -l) )); then
  echo "High RAM: $RAM%" | mail -s "Server Alert" frank@lucy.world
fi
EOF

chmod +x /usr/local/bin/server-monitor.sh

# Run elke 15 minuten
echo "*/15 * * * * /usr/local/bin/server-monitor.sh" | crontab -
```

## 💡 Optimization Tips

### Voor $6 droplet maximaal benutten

```bash
# Memory optimization
echo 'vm.swappiness=10' >> /etc/sysctl.conf
echo 'vm.vfs_cache_pressure=50' >> /etc/sysctl.conf

# Nginx optimization voor kleine server
# Edit /etc/nginx/nginx.conf
worker_processes 1;
worker_connections 512;
```

### Enable swap voor extra memory

```bash
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## 📊 Performance Expectations

### $6/maand (1GB RAM)

- **Users:** 50-100 daily
- **Searches:** 500-1000 daily
- **Response:** 2-5 seconds
- **Uptime:** 99% (manual monitoring)

### $12/maand (2GB RAM)

- **Users:** 100-200 daily  
- **Searches:** 1000-2000 daily
- **Response:** 1-3 seconds
- **Uptime:** 99.5%

### $24/maand (4GB RAM)

- **Users:** 200-500 daily
- **Searches:** 2000-5000 daily
- **Response:** 1-2 seconds
- **Uptime:** 99.8%

## 🚀 Growth Path

```text
$6   → $12  → $24  → $48  → $96
1GB  → 2GB  → 4GB  → 8GB  → 16GB
50   → 200  → 500  → 1K   → 2K users
```

## 💰 Cost-Benefit Analysis

### Upgrade wanneer

- **Revenue per user** > **Extra server kosten**
- **User experience** lijdt onder performance
- **Brand reputation** risico door downtime

### Voorbeeld

- **50 users** paying €5/maand = €250 revenue
- **Server upgrade** €6 → €12 = €6 extra
- **ROI:** Extra €6 voor betere UX = excellent investment

---

Start klein, groei mee met je gebruikers! 📈
