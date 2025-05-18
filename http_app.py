"""
HTTP-only app for Brush Up application
This simple WSGI app works with gunicorn and doesn't require SSL certificates
"""
import os
import subprocess
import sys
import time
from threading import Thread

# Configure environment for Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true'
os.environ['HTTPS'] = 'off'
os.environ['wsgi.url_scheme'] = 'http'

# Fix the CritiqueSerializer if needed
try:
    import fix_critique_serializer
    fix_critique_serializer.add_missing_method()
    print("✓ CritiqueSerializer fixes applied")
except:
    print("! Could not apply CritiqueSerializer fixes - already fixed?")

# Variables for Django subprocess
django_process = None

def start_django():
    """Start Django server in the background"""
    global django_process
    try:
        from fix_karma_db import create_karma_tables
        create_karma_tables()
        print("✓ Verified KarmaEvent table existence")
    except:
        print("! Could not verify KarmaEvent table - likely exists already")
    
    # Close any existing process
    if django_process:
        try:
            django_process.terminate()
            time.sleep(1)
        except:
            pass
    
    # Use Django development server directly (no SSL)
    cmd = [sys.executable, "manage.py", "runserver", "0.0.0.0:8000"]
    print(f"Starting Django with: {' '.join(cmd)}")
    django_process = subprocess.Popen(cmd)
    time.sleep(2)  # Give Django time to start

# Start Django in a separate thread
Thread(target=start_django).start()

# Simple Flask app to proxy requests
from flask import Flask, request, redirect, send_from_directory
import requests

app = Flask(__name__)

@app.route('/')
def index():
    """Redirect to Django app"""
    return redirect("http://localhost:8000/")

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        response = requests.get("http://localhost:8000/", timeout=2)
        return "Django server is running", 200
    except:
        return "Django server is not running", 503

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy(path):
    """Proxy all requests to Django"""
    django_url = f"http://localhost:8000/{path}"
    
    try:
        # Forward the request to Django
        resp = requests.request(
            method=request.method,
            url=django_url,
            headers={key: value for key, value in request.headers if key != 'Host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            params=request.args,
            timeout=5
        )
        
        # Forward the response from Django
        response = app.response_class(
            response=resp.content,
            status=resp.status_code,
            headers=dict(resp.headers)
        )
        
        return response
    except Exception as e:
        return f"Error proxying to Django: {str(e)}", 500

# Gunicorn needs the application object
application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)