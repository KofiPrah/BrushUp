"""
Simple HTTP server for Brush Up application

This script completely disables SSL by removing certificate files and
running Django's development server directly.
"""
import os
import sys
import signal

CERT_DIR = 'certs'
CERT_FILE = os.path.join(CERT_DIR, 'cert.pem')
KEY_FILE = os.path.join(CERT_DIR, 'key.pem')

def signal_handler(sig, frame):
    """Handle termination signals gracefully"""
    print("\nShutting down server...")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def main():
    """Run Django in HTTP-only mode"""
    # Set environment variables
    os.environ['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
    os.environ['PYTHONUNBUFFERED'] = '1'
    os.environ['DJANGO_DEVELOPMENT'] = 'true'
    os.environ['DJANGO_INSECURE'] = 'true'
    os.environ['SSL_ENABLED'] = 'false'
    os.environ['HTTP_ONLY'] = 'true'
    
    # Disable SSL certificates
    os.makedirs(CERT_DIR, exist_ok=True)
    if os.path.exists(CERT_FILE):
        os.rename(CERT_FILE, f"{CERT_FILE}.bak")
    if os.path.exists(KEY_FILE):
        os.rename(KEY_FILE, f"{KEY_FILE}.bak")
    
    # Print banner
    print("\n" + "=" * 70)
    print(" BRUSH UP - HTTP MODE ".center(70, '='))
    print("=" * 70)
    print("Starting Django development server on port 5000")
    print("SSL certificates have been disabled")
    
    # Run Django development server
    from django.core.management import execute_from_command_line
    sys.argv = ['manage.py', 'runserver', '0.0.0.0:5000']
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()