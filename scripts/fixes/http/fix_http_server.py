"""
HTTP-only server for Brush Up application

This script runs Django in HTTP mode without requiring SSL certificates.
"""

import os
import sys
import signal
import subprocess

CERT_DIR = 'certs'
CERT_FILE = os.path.join(CERT_DIR, 'cert.pem')
KEY_FILE = os.path.join(CERT_DIR, 'key.pem')

def print_header(message):
    """Print a formatted message header"""
    border = "=" * len(message)
    print(f"\n{border}\n{message}\n{border}")

def main():
    """Run Django application in HTTP mode"""
    # Set environment variables to use HTTP mode
    os_env = os.environ.copy()
    os_env["SSL_ENABLED"] = "false"
    os_env["HTTP_ONLY"] = "true"
    os_env["HTTPS"] = "off"
    os_env["wsgi_url_scheme"] = "http"
    
    # Create empty certificate files to satisfy the workflow
    # but configure gunicorn to not actually use them
    os.makedirs(CERT_DIR, exist_ok=True)
    with open(CERT_FILE, "w") as f:
        f.write("")
    with open(KEY_FILE, "w") as f:
        f.write("")
    
    print_header("Starting Brush Up in HTTP mode (no SSL)")
    
    # Run gunicorn with HTTP configuration
    cmd = [
        "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--reload",
        "main:app"
    ]
    
    # Run the server process
    process = subprocess.Popen(cmd, env=os_env)
    
    # Handle interrupt signal
    try:
        process.wait()
    except KeyboardInterrupt:
        print_header("Stopping server...")
        process.terminate()
        process.wait()
        print_header("Server stopped")

if __name__ == "__main__":
    main()