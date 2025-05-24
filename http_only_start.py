"""
HTTP-only starter for Brush Up application
Completely bypasses SSL requirements by disabling certificates
"""
import os
import sys
import subprocess

def main():
    # Force HTTP mode
    os.environ['DJANGO_INSECURE'] = 'true'
    os.environ['DJANGO_DEVELOPMENT'] = 'true'
    os.environ['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
    os.environ['SSL_ENABLED'] = 'false'
    os.environ['HTTP_ONLY'] = 'true'
    os.environ['PYTHONUNBUFFERED'] = '1'
    
    # Disable SSL by creating empty certificate files
    if os.path.exists('cert.pem'):
        os.rename('cert.pem', 'cert.pem.disabled')
    if os.path.exists('key.pem'):
        os.rename('key.pem', 'key.pem.disabled')
    
    # Create empty certificate files
    with open('cert.pem', 'w') as f:
        f.write('')
    with open('key.pem', 'w') as f:
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