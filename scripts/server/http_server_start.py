#!/usr/bin/env python3
"""
Simple HTTP-only server for Brush Up application
This script runs the Django application without SSL to fix common issues
"""

import os
import sys
import signal
import subprocess

def print_header(message):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {message} ".center(80, "="))
    print("=" * 80 + "\n")

def signal_handler(sig, frame):
    """Handle termination signals gracefully"""
    print_header("Shutting down Brush Up application")
    sys.exit(0)

def main():
    """Main function to run the HTTP server"""
    # Register signal handlers for clean shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Clear the SSL certificate files to ensure they don't interfere
    with open('cert.pem.disabled', 'w') as f:
        f.write('DISABLED')
    with open('key.pem.disabled', 'w') as f:
        f.write('DISABLED')
    
    # Set up HTTP environment
    os.environ['HTTPS'] = 'off'
    os.environ['HTTP_MODE'] = 'true'
    os.environ['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
    
    print_header("Starting Brush Up in HTTP-only mode")
    
    # Run the Django development server
    cmd = [sys.executable, "manage.py", "runserver", "0.0.0.0:8000"]
    process = subprocess.Popen(cmd)
    
    try:
        process.wait()
    except KeyboardInterrupt:
        print_header("Shutting down...")
        process.terminate()
        process.wait()

if __name__ == "__main__":
    main()