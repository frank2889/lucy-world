"""WSGI entrypoint for DigitalOcean App Platform / Gunicorn."""
from backend import create_app

application = create_app()
app = application  # gunicorn default expects `app`
