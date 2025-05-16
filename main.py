import os
from artcritique.wsgi import application
from flask import Flask, redirect

# For Gunicorn - Django WSGI Application
app = application

# Also provide a Flask application to handle specific routes
flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    """Redirect to the Django app"""
    return redirect('/admin/')

@flask_app.route('/health')
def health():
    """Health check endpoint"""
    return {"status": "healthy"}

# Check if we're in deployment mode (via environment variable)
# This allows us to switch between local development (with SSL) and deployment (without SSL)
ssl_enabled = os.environ.get('SSL_ENABLED', 'false').lower() == 'true'
# Force disable SSL for testing
ssl_enabled = False

if not ssl_enabled:
    # Configure Django to run in plain HTTP mode
    # Replit's load balancer will handle HTTPS automatically
    print("Running in HTTP mode (SSL handled by Replit's load balancer)")
else:
    # Configure Django to use HTTPS for local development
    print("Running in HTTPS mode with local SSL termination")