# WSGI entrypoint for DigitalOcean App Platform / Gunicorn
from app import app as application

# Gunicorn looks for a variable named `app` by default; keep both names
app = application
