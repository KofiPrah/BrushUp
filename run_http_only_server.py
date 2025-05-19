#!/usr/bin/env python3
"""
HTTP-only server for Brush Up application
Fixes SSL issues with Replit's load balancer
"""

import os
import subprocess
import sys
import time
import signal

def print_banner(message):
    """Print a formatted banner message"""
    width = len(message) + 4
    print("\n" + "=" * width)
    print(f"  {message}")
    print("=" * width + "\n")

def handle_signal(sig, frame):
    """Handle termination signals gracefully"""
    print("\nShutting down server...")
    sys.exit(0)

def main():
    """Run the server in HTTP-only mode"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    print_banner("Setting up HTTP-only server")
    
    # Kill any existing server processes
    subprocess.run("pkill -f 'gunicorn|runserver' || true", shell=True)
    
    # Make empty SSL certificates
    for filename in ['cert.pem', 'key.pem']:
        with open(filename, 'w') as f:
            f.write("")
    
    # Start the server in HTTP-only mode
    print_banner("Starting HTTP-only server")
    
    # Set environment variables for HTTP mode
    env = os.environ.copy()
    env['SSL_ENABLED'] = 'false'
    env['HTTPS'] = 'off'
    env['wsgi.url_scheme'] = 'http'
    env['SECURE_SSL_REDIRECT'] = 'false'
    
    # Run gunicorn without SSL parameters
    cmd = [
        "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--reuse-port",
        "--reload",
        "main:app"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print("\nServer shutdown requested")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())