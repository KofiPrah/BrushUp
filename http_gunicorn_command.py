#!/usr/bin/env python3
"""
HTTP server configuration for Art Critique
Runs gunicorn in HTTP mode without SSL certificates
"""
import os
import subprocess
import sys

# Set environment variables for HTTP mode
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"
os.environ["DJANGO_SETTINGS_MODULE"] = "artcritique.settings"

if __name__ == "__main__":
    # Build the gunicorn command without SSL parameters
    command = [
        "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--workers", "1",
        "--timeout", "120",
        "--reload",
        "--worker-class", "sync",
        "--log-level", "info",
        "artcritique.wsgi:application"
    ]
    
    print("Starting Art Critique in HTTP mode...")
    print("Command:", " ".join(command))
    
    # Run gunicorn
    process = subprocess.run(command)
    sys.exit(process.returncode)