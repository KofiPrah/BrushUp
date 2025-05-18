#!/usr/bin/env python3
"""
HTTP-only server for Brush Up application
This script removes SSL certificate requirements from gunicorn
"""
import os
import subprocess
import sys

def print_banner(message):
    """Print a message in a visible banner"""
    print("\n" + "=" * 60)
    print(f" {message}")
    print("=" * 60 + "\n")

def main():
    # Kill any existing server processes
    print_banner("Stopping any existing servers")
    os.system("pkill -f 'gunicorn|runserver' || true")
    
    # Create empty certificate files
    print_banner("Creating empty certificate files")
    for filename in ['cert.pem', 'key.pem']:
        with open(filename, 'w') as f:
            f.write("")
        print(f"Created empty {filename}")

    # Set environment variables for HTTP mode
    print_banner("Setting up HTTP-only environment")
    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
    env['SSL_ENABLED'] = 'false'
    env['HTTP_ONLY'] = 'true'
    env['HTTPS'] = 'off'
    env['wsgi.url_scheme'] = 'http'

    # Start gunicorn without SSL certificates
    print_banner("Starting HTTP-only server")
    
    # Command to run gunicorn without SSL
    cmd = [
        "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--reload",
        "main:app"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    try:
        # Use subprocess.run to wait for the process to complete
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print("\nShutting down server")
        sys.exit(0)

if __name__ == "__main__":
    main()