# Gunicorn configuration file - Optimized for DigitalOcean App Platform
import os

bind = f"0.0.0.0:{os.environ.get('PORT', 8080)}"
wsgi_app = "scripts.wsgi:app"
workers = 2  # Good for App Platform basic tier
worker_class = "sync"
worker_connections = 500
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
reload = False

# Logging
# Disable Gunicorn access logs to reduce DigitalOcean runtime log volume.
accesslog = None
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "lucy-world-search"

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"


def on_starting(server):
    server.log.info("Starting Lucy World Search Gunicorn workers")
