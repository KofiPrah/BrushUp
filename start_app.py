#!/usr/bin/env python3
"""
Starter script for Brush Up application
Properly configures the Django application to run in HTTP mode
"""

import os
import sys
import subprocess

def print_banner(message):
    """Print a formatted banner message"""
    print("\n" + "=" * 60)
    print(f"  {message}")
    print("=" * 60 + "\n")

def main():
    """Run the application with proper configuration"""
    print_banner("CONFIGURING HTTP SERVER")
    
    # Disable SSL completely by creating empty certificate files
    for cert_file in ['cert.pem', 'key.pem']:
        with open(cert_file, 'w') as f:
            f.write("")
        print(f"Created empty {cert_file}")
    
    # Kill any existing server processes
    print("Stopping any existing servers...")
    subprocess.run("pkill -f 'gunicorn|runserver' || true", shell=True)
    
    # Set up environment variables for HTTP mode
    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
    env['SSL_ENABLED'] = 'false'
    env['HTTP_ONLY'] = 'true'
    env['wsgi.url_scheme'] = 'http'
    env['SECURE_SSL_REDIRECT'] = 'false'
    
    # Command to run Django without SSL
    cmd = [
        "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--reload",
        "artcritique.wsgi:application"
    ]
    
    print_banner("STARTING SERVER")
    print(f"Running: {' '.join(cmd)}")
    
    # Execute command with the HTTP environment
    try:
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print("\nServer shutdown requested")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())