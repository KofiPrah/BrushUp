#!/usr/bin/env python3
"""
Start Brush Up application in HTTP-only mode
This avoids SSL certificate errors in Replit
"""

import os
import sys
import subprocess
import signal

def signal_handler(sig, frame):
    """Handle termination signals"""
    print("\nShutting down server...")
    sys.exit(0)

def main():
    """Run the server in HTTP mode"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("\n=== Starting Brush Up in HTTP-only mode ===\n")
    
    # Kill any existing server processes
    subprocess.run("pkill -f 'gunicorn|runserver' || true", shell=True)
    
    # Create empty certificate files
    for filename in ['cert.pem', 'key.pem']:
        with open(filename, 'w') as f:
            f.write("")
    
    # Configure environment for HTTP-only mode
    env = os.environ.copy()
    env["DJANGO_SETTINGS_MODULE"] = "artcritique.settings"
    env["SSL_ENABLED"] = "false"
    env["HTTP_ONLY"] = "true"
    env["HTTPS"] = "off"
    
    # Start Django with gunicorn in HTTP mode
    cmd = [
        "gunicorn",
        "--bind", "0.0.0.0:5000",
        "artcritique.wsgi:application"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print("\nServer shutdown requested")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())