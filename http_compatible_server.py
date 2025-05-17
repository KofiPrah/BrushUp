"""
HTTP-compatible server for Art Critique

This script runs the application in a way that's compatible with Replit's environment,
handling both HTTP and HTTPS requests appropriately.
"""
import os
import sys
import subprocess

# Set environment variables to make sure Django and other services
# operate correctly in the Replit environment
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"

# Start the Django application using Gunicorn, configured for HTTP compatibility
from flask import Flask, redirect

app = Flask(__name__)

@app.route('/')
def index():
    """Redirect to the Django app"""
    return redirect('/critique/')

@app.route('/health')
def health():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    print("Starting Art Critique in HTTP-compatible mode...")
    # Import the Django WSGI application
    from artcritique.wsgi import application as django_app
    
    # Set the app variable for Gunicorn to use
    app = django_app
    
    # Run directly when using `python http_compatible_server.py`
    app.run(host='0.0.0.0', port=5000)