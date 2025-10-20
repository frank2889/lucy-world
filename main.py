#!/usr/bin/env python3
"""Direct app entrypoint for DigitalOcean App Platform."""
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend import create_app

# Create the Flask app
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)