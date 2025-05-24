"""
Simple HTTP-only script for Brush Up
Disables SSL certificates and runs Django development server directly
"""
import os
import sys
import signal
import subprocess

def main():
    # Disable SSL by moving certificates
    if os.path.exists('cert.pem'):
        os.rename('cert.pem', 'cert.pem.disabled')
    if os.path.exists('key.pem'):
        os.rename('key.pem', 'key.pem.disabled')
    
    # Create empty certificate files
    with open('cert.pem', 'w') as f:
        f.write('')
    with open('key.pem', 'w') as f:
        f.write('')
    
    # Print banner
    print("\n" + "=" * 70)
    print(" Starting Brush Up in HTTP-only mode ".center(70, '='))
    print("=" * 70 + "\n")
    
    # Run Django development server
    cmd = [sys.executable, 'manage.py', 'runserver', '0.0.0.0:5000']
    
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'
    env['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
    
    try:
        process = subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print("\nShutting down...\n")

if __name__ == "__main__":
    main()