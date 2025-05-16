"""
Simple script to run the Django application over HTTP (no SSL).
This is needed for compatibility with Replit's load balancer.
"""

import os
import sys
import subprocess

def main():
    """Run Gunicorn server without SSL"""
    print("Starting HTTP-only server...")
    
    # Force HTTP mode
    os.environ['SSL_ENABLED'] = 'false'
    
    # Run Gunicorn without SSL
    cmd = [
        "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--reload",
        "--access-logfile", "-",
        "--error-logfile", "-",
        "main:app"
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()