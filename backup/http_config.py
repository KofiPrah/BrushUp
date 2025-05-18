#!/usr/bin/env python3
"""
HTTP configuration for Brush Up application

This script configures gunicorn to run in HTTP mode to work with Replit's load balancer.
"""

import os
import sys
from flask import Flask, redirect

# Create Flask app for HTTP compatibility
app = Flask(__name__)

# Set environment variables
os.environ["DJANGO_SETTINGS_MODULE"] = "artcritique.settings"
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"

# Basic routes for health checks
@app.route('/')
def index():
    """Redirect to Django app"""
    return redirect('/critique/')

@app.route('/health')
def health():
    """Health check endpoint"""
    return 'OK'

if __name__ == "__main__":
    # Run the Flask app in HTTP mode
    app.run(host="0.0.0.0", port=5000)