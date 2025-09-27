# Gunicorn configuration file - Optimized for 1GB RAM / 1 vCPU droplet
bind = "0.0.0.0:8000"
workers = 2  # Conservative for 1GB RAM
worker_class = "sync"
worker_connections = 500  # Lower connection limit for small server
timeout = 30  # Standard timeout
keepalive = 2  # Basic connection reuse
max_requests = 1000  # Standard request limit
max_requests_jitter = 100  # Standard jitter
preload_app = True
reload = False

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "lucy-world-search"

# Server mechanics
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"