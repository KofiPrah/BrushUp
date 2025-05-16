"""
HTTP-only version of the main application entry point.
This version is specifically designed to work with Replit's HTTP load balancer.
"""

import os
import ssl
from artcritique.wsgi import application

# For Gunicorn - Django WSGI Application
app = application

# Force SSL to be disabled by setting the environment variable
os.environ['SSL_ENABLED'] = 'false'
os.environ['SECURE_SSL_REDIRECT'] = 'false'

# Patch SSL to prevent SSL wrapping
def disable_ssl():
    """
    Disables SSL functionality to ensure the server operates in HTTP-only mode.
    This is needed because Replit's load balancer expects HTTP but Gunicorn uses HTTPS.
    """
    # Monkeypatch SSLContext creation to prevent SSL initialization
    original_sslcontext = ssl.SSLContext
    class DummySSLContext:
        def __init__(self, *args, **kwargs):
            print("HTTP-only mode: Creating dummy SSL context")
        
        def load_cert_chain(self, *args, **kwargs):
            print("HTTP-only mode: Skipping certificate loading")
            return None
            
        def wrap_socket(self, sock, *args, **kwargs):
            print("HTTP-only mode: Bypassing SSL socket wrapping")
            return sock
    
    # Apply the patch
    ssl.SSLContext = DummySSLContext
    print("HTTP-only mode: SSL disabled")

# Apply the SSL patch
disable_ssl()

# Also provide a Flask application for health checks
from flask import Flask, redirect

flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    """Redirect to the Django app"""
    return redirect('/admin/')

@flask_app.route('/health')
def health():
    """Health check endpoint"""
    return {"status": "healthy"}