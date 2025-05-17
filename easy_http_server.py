#!/usr/bin/env python3
"""
Simple HTTP-only server for Brush Up
Uses Flask to provide a simple HTTP server that works with Replit
"""
import os
from flask import Flask, redirect, Response
from flask_cors import CORS
import subprocess
import threading
import time

# Create a Flask app
app = Flask(__name__)
CORS(app)

# Set environment variables
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"
os.environ["DJANGO_SETTINGS_MODULE"] = "artcritique.settings"

# Define Django process
django_process = None

def start_django():
    """Start Django as a subprocess"""
    global django_process
    # Run Django development server in the background
    django_process = subprocess.Popen(
        ["python", "manage.py", "runserver", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    print("Django server started on port 8000")

# Start Django in a separate thread
threading.Thread(target=start_django, daemon=True).start()

# Wait for Django to start
time.sleep(2)

@app.route('/')
def index():
    """Redirect to Django app"""
    return redirect('http://localhost:8000/critique/')

@app.route('/health')
def health():
    """Health check endpoint"""
    return 'OK'

@app.route('/<path:path>')
def proxy(path):
    """Proxy all other requests to Django"""
    import requests
    resp = requests.get(f'http://localhost:8000/{path}')
    return Response(
        resp.content,
        status=resp.status_code,
        content_type=resp.headers['content-type']
    )

if __name__ == '__main__':
    print("Starting HTTP-only server for Brush Up...")
    app.run(host='0.0.0.0', port=5000)