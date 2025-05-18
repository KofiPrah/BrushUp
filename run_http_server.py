"""
HTTP Server for Brush Up application
Run Django in HTTP mode without SSL configuration
"""

import os
import sys
import subprocess
import time
import signal

def print_banner(message):
    """Print a formatted banner message"""
    line = "=" * len(message)
    print(f"\n{line}\n{message}\n{line}")

def signal_handler(sig, frame):
    """Handle termination signals"""
    print_banner("Shutting down HTTP server...")
    if 'django_process' in globals():
        django_process.terminate()
    sys.exit(0)

def main():
    """Run Django directly in HTTP mode"""
    # Configure signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Set environment variables for HTTP mode
    env = os.environ.copy()
    env['SSL_ENABLED'] = 'false'
    env['HTTP_ONLY'] = 'true'
    env['HTTPS'] = 'off'
    env['wsgi.url_scheme'] = 'http'
    
    # Start Django with gunicorn in HTTP mode (no SSL)
    print_banner("Starting Brush Up in HTTP mode")
    
    cmd = [
        sys.executable, '-m', 'gunicorn',
        '--bind', '0.0.0.0:5000',
        '--reload',
        'main:app'
    ]
    
    global django_process
    django_process = subprocess.Popen(cmd, env=env)
    
    try:
        django_process.wait()
    except KeyboardInterrupt:
        print_banner("Keyboard interrupt received")
        django_process.terminate()
        django_process.wait()
        print_banner("Server stopped")

if __name__ == "__main__":
    main()