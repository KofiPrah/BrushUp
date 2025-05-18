#!/usr/bin/env python
"""
Simple HTTP server for Brush Up application

This script:
1. Creates empty SSL certificate files (if they don't exist)
2. Starts Django with gunicorn in HTTP-only mode
"""
import os
import subprocess
import sys

def main():
    """Create empty certificates and run the server"""
    # Create empty cert files to avoid gunicorn errors
    if not os.path.exists('cert.pem'):
        with open('cert.pem', 'w') as f:
            f.write('')
    
    if not os.path.exists('key.pem'):
        with open('key.pem', 'w') as f:
            f.write('')
            
    # Print status message
    print("Starting Brush Up in HTTP-only mode...")
    
    # Run HTTP-only server
    cmd = [
        "python", "-m", "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--reload",
        "main:app"
    ]
    
    # Start the server
    process = subprocess.run(cmd)
    return process.returncode

if __name__ == "__main__":
    sys.exit(main())