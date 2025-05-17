"""
HTTP-only entry point for the Art Critique application.
This module provides compatibility with Replit's load balancer by
running in HTTP mode (without SSL certificates).
"""
import os
import http_server_settings  # Apply HTTP settings first

# Now import the WSGI application
from artcritique.wsgi import application
from flask import Flask, redirect

# Set up the WSGI application
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

# Print a confirmation message
print("HTTP-only main module loaded")
print("Using S3 storage:", os.environ.get("USE_S3", "False"))
print("HTTP mode enabled:", os.environ.get("HTTP_ONLY", "False"))