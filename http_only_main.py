#!/usr/bin/env python3
"""
HTTP-only main entry point for Brush Up application
This version runs in plain HTTP mode for compatibility with Replit
"""
import os
import sys

# Configure for HTTP-only mode
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"
os.environ["DJANGO_SETTINGS_MODULE"] = "artcritique.settings"

# Import Flask for a simple wrapper app
from flask import Flask, redirect

# Create a simple Flask app as the WSGI entry point
app = Flask(__name__)

@app.route('/')
def index():
    """Redirect to the Django app"""
    return redirect('/critique/')

@app.route('/health')
def health():
    """Health check endpoint"""
    return 'OK'

# For direct execution (not via gunicorn)
if __name__ == "__main__":
    print("Starting Brush Up application in HTTP mode...")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)