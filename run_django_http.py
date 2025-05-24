#!/usr/bin/env python3
"""
Simple HTTP-only server for Brush Up application

This script disables SSL certificates and runs Django directly 
without them to fix the 403 Forbidden errors.
"""

import os
import sys
import subprocess

def main():
    # Disable SSL by removing or emptying the certificate files
    if os.path.exists('cert.pem'):
        os.rename('cert.pem', 'cert.pem.disabled')
    if os.path.exists('key.pem'):
        os.rename('key.pem', 'key.pem.disabled')

    # Create empty certificate files so other code doesn't break
    with open('cert.pem', 'w') as f:
        f.write('')
    with open('key.pem', 'w') as f:
        f.write('')
    
    # Set HTTP environment variables
    os.environ['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
    os.environ['PYTHONUNBUFFERED'] = '1'
    os.environ['HTTP_MODE'] = 'true'
    
    print("=" * 80)
    print("Starting Brush Up in HTTP-only mode...")
    print("=" * 80)
    
    # Run Django with Gunicorn without SSL
    cmd = [
        'gunicorn',
        '--bind', '0.0.0.0:5000',
        '--reuse-port',
        '--reload',
        'main:app'
    ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nShutting down...")

if __name__ == "__main__":
    main()