"""
HTTP-only starter for Brush Up application
Completely bypasses SSL requirements by disabling certificates
"""
import os
import sys
import subprocess

CERT_DIR = 'certs'
CERT_FILE = os.path.join(CERT_DIR, 'cert.pem')
KEY_FILE = os.path.join(CERT_DIR, 'key.pem')

def main():
    # Force HTTP mode
    os.environ['DJANGO_INSECURE'] = 'true'
    os.environ['DJANGO_DEVELOPMENT'] = 'true'
    os.environ['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
    os.environ['SSL_ENABLED'] = 'false'
    os.environ['HTTP_ONLY'] = 'true'
    os.environ['PYTHONUNBUFFERED'] = '1'
    
    # Disable SSL by creating empty certificate files
    os.makedirs(CERT_DIR, exist_ok=True)
    if os.path.exists(CERT_FILE):
        os.rename(CERT_FILE, f"{CERT_FILE}.disabled")
    if os.path.exists(KEY_FILE):
        os.rename(KEY_FILE, f"{KEY_FILE}.disabled")

    # Create empty certificate files
    with open(CERT_FILE, 'w') as f:
        f.write('')
    with open(KEY_FILE, 'w') as f:
        f.write('')
    
    # Print startup message
    print("\n" + "=" * 70)
    print(" BRUSH UP - HTTP ONLY SERVER ".center(70, '='))
    print("=" * 70)
    
    # Run Django directly using manage.py
    cmd = [sys.executable, 'manage.py', 'runserver', '0.0.0.0:5000']
    process = subprocess.run(cmd)
    
if __name__ == "__main__":
    main()