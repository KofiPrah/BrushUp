#!/usr/bin/env python3
"""
Run Brush Up application with Gunicorn in HTTP mode (no SSL)
This script creates a gunicorn server without SSL certificates for Replit compatibility
"""
import os
import sys
import subprocess

def main():
    """Run HTTP server for Brush Up"""
    print("Starting Brush Up (formerly Art Critique) in HTTP mode...")
    
    # Set environment variables
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artcritique.settings")
    os.environ["SSL_ENABLED"] = "false"
    os.environ["HTTP_ONLY"] = "true"
    
    # Run with gunicorn without SSL certificates
    cmd = [
        "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--worker-class", "sync",
        "--workers", "1",
        "--timeout", "120",
        "--reload",
        # Important: don't include --certfile or --keyfile
        "artcritique.wsgi:application"
    ]
    
    # Run the server
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nShutting down server...")
        sys.exit(0)

if __name__ == "__main__":
    main()