"""
HTTP-only starter for Brush Up application
Runs Django without SSL requirements
"""
import os
import sys
import signal
import subprocess

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

def main():
    # Print banner
    print("\n" + "=" * 70)
    print(" BRUSH UP - HTTP MODE ".center(70, '='))
    print("=" * 70)
    
    # Disable SSL by making empty certificate files
    os.makedirs(CERT_DIR, exist_ok=True)
    with open(CERT_FILE, 'w') as f:
        f.write('')
    with open(KEY_FILE, 'w') as f:
        f.write('')
    
    # Set environment variables
    os.environ['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
    os.environ['DJANGO_DEVELOPMENT'] = 'true'
    os.environ['DJANGO_INSECURE'] = 'true'
    os.environ['SSL_ENABLED'] = 'false'
    os.environ['HTTP_ONLY'] = 'true'
    
    # Start Django directly with runserver
    cmd = [sys.executable, 'manage.py', 'runserver', '0.0.0.0:5000']
    env = os.environ.copy()
    
    # Run the server
    print("Starting Django development server on port 5000")
    print("SSL certificates have been disabled")
    
    try:
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print("\nServer shut down")

if __name__ == "__main__":
    main()