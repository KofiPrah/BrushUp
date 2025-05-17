#!/usr/bin/env python3
"""
HTTP-only runner for Brush Up application

This script runs Django with gunicorn in HTTP mode (no SSL certificates)
to work correctly in the Replit environment.
"""
import os
import sys
import subprocess

# Configure the environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artcritique.settings")
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"

# Update CORS and CSRF settings for Replit
REPLIT_DOMAIN = os.environ.get("REPLIT_DOMAIN", "")

def main():
    """Run Django with gunicorn in HTTP mode"""
    # Build the gunicorn command (no SSL certificates)
    cmd = [
        "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--workers", "1",
        "--timeout", "120",
        "--reload",
        "artcritique.wsgi:application"
    ]
    
    # Print startup message
    print(f"Starting Brush Up (formerly Art Critique) in HTTP mode...")
    print(f"Running on: {REPLIT_DOMAIN}")
    
    # Run the server
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Error running server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()