# Production Configuration voor 8GB RAM / 4 vCPU DigitalOcean Droplet

## Server Optimizations

### Nginx Worker Processes
```nginx
# /etc/nginx/nginx.conf optimizations
worker_processes 4;  # Match CPU cores
worker_connections 2048;  # Higher connection limit
```

### System Limits
```bash
# Add to /etc/security/limits.conf
www-data soft nofile 65536
www-data hard nofile 65536
```

### Memory Management
```bash
# System swap configuration (recommended for 8GB RAM)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Redis Cache (Optional)
```bash
# Redis configuration for caching keyword results
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Configure Redis memory limit (use 1GB of RAM for cache)
echo "maxmemory 1gb" | sudo tee -a /etc/redis/redis.conf
echo "maxmemory-policy allkeys-lru" | sudo tee -a /etc/redis/redis.conf
sudo systemctl restart redis-server
```

## Performance Monitoring

### Real-time Monitoring
```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs glances

# Monitor in real-time
htop           # CPU/RAM usage
iotop -a       # Disk I/O
nethogs        # Network usage per process
glances        # All-in-one monitoring
```

### Log Monitoring
```bash
# Monitor application performance
sudo journalctl -u lucy-world-search -f | grep -E "(ERROR|WARNING|performance)"

# Monitor Nginx performance
sudo tail -f /var/log/nginx/access.log | grep -E "(POST|GET)"
```

## Expected Performance

### With 8GB RAM / 4 vCPU:
- **Concurrent Users**: 500-1000 active users
- **Requests per Second**: 100-200 RPS
- **Keyword Processing**: 50-100 simultaneous searches
- **Response Time**: <2 seconds for most requests
- **Uptime**: 99.9% availability

### Resource Usage:
- **RAM Usage**: 2-4GB under normal load
- **CPU Usage**: 20-40% average
- **Disk I/O**: Minimal (mainly logs)
- **Network**: 10-50 Mbps depending on traffic

## Scaling Options

### Vertical Scaling (Same Droplet):
- Upgrade to 16GB RAM ($128/month) for 2x capacity
- Add more Gunicorn workers (up to 16)

### Horizontal Scaling (Multiple Droplets):
- Load balancer + 2-3 app servers
- Separate database server
- CDN for static files

## Cost Analysis

### $64/month Droplet Benefits:
- **Performance**: 10x better than $6 droplet
- **Reliability**: Better resource headroom
- **Scalability**: Room to grow
- **Professional**: Production-ready specs

### ROI Calculation:
- Support 500+ daily active users
- Process 10,000+ keyword searches/day
- Handle traffic spikes without downtime
- Professional image for lucy.world brand