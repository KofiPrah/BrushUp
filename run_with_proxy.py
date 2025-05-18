#!/usr/bin/env python3
"""
Run the Django app with an HTTP proxy for testing
"""
import os
import sys
import subprocess
import signal
import time
import threading

# Django process
django_process = None

def signal_handler(sig, frame):
    """Handle termination signals"""
    print("\nShutting down servers...")
    
    if django_process:
        django_process.terminate()
        try:
            django_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            django_process.kill()
    
    sys.exit(0)

def start_django():
    """Start Django in HTTP mode"""
    global django_process
    
    # Set Django environment variables
    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
    env['SSL_ENABLED'] = 'false'
    env['HTTP_ONLY'] = 'true'
    
    # Create empty SSL certificates (required by workflow)
    for filename in ['cert.pem', 'key.pem']:
        if not os.path.exists(filename):
            with open(filename, 'w') as f:
                f.write("")
            print(f"Created empty {filename}")
    
    # Start Django without SSL
    cmd = ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
    print(f"Starting server: {' '.join(cmd)}")
    
    django_process = subprocess.Popen(cmd, env=env)
    return django_process

if __name__ == "__main__":
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start Django
    django_proc = start_django()
    
    # Wait for process to finish
    try:
        django_proc.wait()
    except KeyboardInterrupt:
        signal_handler(None, None)