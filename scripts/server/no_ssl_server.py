"""
Simple HTTP-only server for Django

This script removes the SSL certificates and starts Django in HTTP mode.
"""
import os
import sys
import django
import subprocess
import signal
import time

def main():
    """Run Django in HTTP mode without SSL"""
    # Set Django environment variables
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
    os.environ['PYTHONUNBUFFERED'] = '1'
    os.environ['DJANGO_DEVELOPMENT'] = 'true'
    os.environ['DEBUG'] = 'true'
    
    # Print banner
    print("\n" + "=" * 70)
    print(" BRUSH UP - HTTP ONLY SERVER ".center(70, '='))
    print("=" * 70)
    
    # Make sure we don't use SSL
    if os.path.exists('cert.pem'):
        os.rename('cert.pem', 'cert.pem.bak')
        print("Renamed cert.pem to cert.pem.bak")
    
    if os.path.exists('key.pem'):
        os.rename('key.pem', 'key.pem.bak')
        print("Renamed key.pem to key.pem.bak")
    
    # Start Django server directly
    cmd = [sys.executable, 'manage.py', 'runserver', '0.0.0.0:5000']
    process = subprocess.Popen(cmd)
    
    # Handle SIGINT and SIGTERM signals
    def signal_handler(sig, frame):
        print("\nShutting down server...")
        process.terminate()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Wait for the process to complete
    try:
        process.wait()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        process.terminate()

if __name__ == "__main__":
    main()