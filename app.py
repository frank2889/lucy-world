#!/usr/bin/env python3
"""Wrapper that exposes the Flask app instance for gunicorn and local dev."""
import os
from backend import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.logger.info(f"Starting Lucy World Search on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)