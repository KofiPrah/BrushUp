"""
Django HTTP Server for Brush Up
Runs Django directly without any SSL certificates
"""
import os
import sys
import signal

CERT_DIR = 'certs'
CERT_FILE = os.path.join(CERT_DIR, 'cert.pem')
KEY_FILE = os.path.join(CERT_DIR, 'key.pem')

# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    print("\nShutting down server...")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def run_server():
    # Make sure we're using Django's runserver directly without gunicorn
    os.environ['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
    os.environ['PYTHONUNBUFFERED'] = '1'
    os.environ['DJANGO_DEVELOPMENT'] = 'true'
    os.environ['DJANGO_DEBUG'] = 'true'
    
    # Print banner
    print("\n" + "=" * 70)
    print(" BRUSH UP - HTTP SERVER ".center(70, '='))
    print("=" * 70)
    print("Starting Django development server on port 5000")
    
    # Make empty certificate files to avoid errors
    os.makedirs(CERT_DIR, exist_ok=True)
    if os.path.exists(CERT_FILE):
        os.rename(CERT_FILE, f"{CERT_FILE}.bak")
    if os.path.exists(KEY_FILE):
        os.rename(KEY_FILE, f"{KEY_FILE}.bak")
    
    # Directly use Django's runserver
    from django.core.management import execute_from_command_line
    
    # Run the server
    sys.argv = ['manage.py', 'runserver', '0.0.0.0:5000']
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    run_server()