#!/usr/bin/env python3
"""
HTTP-only entry point for Brush Up application
Simplified HTTP server that works reliably in Replit environment
"""
import os
import sys
from flask import Flask, redirect, send_from_directory

# Create Flask app
app = Flask(__name__)

# Set Django environment variables
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artcritique.settings")
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"

# Configure standard port
PORT = 5000

# Import Django for direct integration
import django
django.setup()

# Import Django views directly
from django.core.wsgi import get_wsgi_application
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# Create a combined application
application = DispatcherMiddleware(
    app,  # Flask app for root
    {
        '': get_wsgi_application()  # Django app
    }
)

@app.route('/static/<path:path>')
def static_files(path):
    """Serve static files"""
    return send_from_directory('staticfiles', path)

@app.route('/health')
def health():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    # Run the app
    app.run(host="0.0.0.0", port=PORT)
else:
    # Export for gunicorn
    app = application