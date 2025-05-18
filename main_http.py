"""
HTTP-only server for Brush Up application

This script fixes the CritiqueSerializer and runs Django in HTTP mode.
"""
import os
import sys
import django
from flask import Flask, request, redirect
import subprocess
import logging
import time
import re
import signal

# Set environment variables for HTTP mode
os.environ['HTTPS'] = 'off'
os.environ['wsgi.url_scheme'] = 'http'
os.environ['HTTP_ONLY'] = 'true'
os.environ['SSL_ENABLED'] = 'false'

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')

# Initialize Django
django.setup()

# Fix missing get_reactions_count method in CritiqueSerializer
try:
    from critique.api.serializers import CritiqueSerializer, CritiqueListSerializer
    
    # Define the get_reactions_count method for both serializer classes
    def get_reactions_count(self, obj):
        """Return the total count of all reactions for this critique."""
        return {
            'HELPFUL': obj.reactions.filter(reaction_type='HELPFUL').count(),
            'INSPIRING': obj.reactions.filter(reaction_type='INSPIRING').count(),
            'DETAILED': obj.reactions.filter(reaction_type='DETAILED').count(),
            'TOTAL': obj.reactions.count()
        }
    
    # Check if the method exists in each serializer and add it if it doesn't
    if not hasattr(CritiqueSerializer, 'get_reactions_count'):
        setattr(CritiqueSerializer, 'get_reactions_count', get_reactions_count)
        print("✓ Added get_reactions_count method to CritiqueSerializer")
    
    if not hasattr(CritiqueListSerializer, 'get_reactions_count'):
        setattr(CritiqueListSerializer, 'get_reactions_count', get_reactions_count)
        print("✓ Added get_reactions_count method to CritiqueListSerializer")
        
    print("✓ Successfully fixed CritiqueSerializer methods")
except Exception as e:
    print(f"! Warning: Error fixing CritiqueSerializer: {e}")

# Check/create database tables if needed
try:
    from django.db import connection
    
    def check_table_exists(table_name):
        """Check if a table exists in the database"""
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name=%s)",
                [table_name]
            )
            return cursor.fetchone()[0]
    
    tables_to_check = ['critique_karmaevent', 'critique_reaction']
    for table in tables_to_check:
        exists = check_table_exists(table)
        if not exists:
            print(f"! Table {table} does not exist. Running Django migrations...")
            from django.core.management import execute_from_command_line
            execute_from_command_line(['manage.py', 'migrate'])
            break
        print(f"✓ Table {table} exists")
except Exception as e:
    print(f"! Warning: Could not check database tables: {e}")

# Create Flask app for HTTP proxy
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "brushup-secret-key")

# Django subprocess
django_process = None
DJANGO_PORT = 8000

def start_django():
    """Start Django server as a subprocess"""
    global django_process
    if django_process:
        # Kill existing process if it exists
        try:
            os.kill(django_process.pid, signal.SIGTERM)
        except:
            pass
    
    # Start Django on a local port
    cmd = [
        sys.executable, 'manage.py', 'runserver', 
        '--noreload', f'127.0.0.1:{DJANGO_PORT}'
    ]
    django_process = subprocess.Popen(cmd)
    print(f"✓ Started Django server on port {DJANGO_PORT}")
    
    # Wait for Django to start
    time.sleep(2)

# Start Django when Flask starts
start_django()

@app.route('/')
def index():
    """Redirect to Django app"""
    path = request.full_path[1:]  # Remove leading slash
    target = f'http://127.0.0.1:{DJANGO_PORT}/{path}'
    return redirect(target)

@app.route('/health')
def health():
    """Health check endpoint"""
    return "OK", 200

@app.route('/<path:path>')
def proxy(path):
    """Proxy all requests to Django"""
    from urllib import request as urllib_request
    import urllib.error
    
    # Construct target URL
    query = request.query_string.decode() if request.query_string else ''
    target = f'http://127.0.0.1:{DJANGO_PORT}/{path}'
    if query:
        target += f'?{query}'
    
    # Copy request headers
    headers = {}
    for header, value in request.headers:
        if header.lower() not in ('host',):
            headers[header] = value
    
    # Create request object
    req = urllib_request.Request(
        target, 
        data=request.get_data(),
        headers=headers,
        method=request.method
    )
    
    try:
        # Execute request
        response = urllib_request.urlopen(req)
        
        # Get response
        response_data = response.read()
        
        # Copy response headers
        headers = {}
        for header, value in response.getheaders():
            if header.lower() not in ('transfer-encoding', 'connection'):
                headers[header] = value
        
        # Return response
        return response_data, response.status, headers
    except urllib.error.HTTPError as e:
        return e.read(), e.code, dict(e.headers)
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)