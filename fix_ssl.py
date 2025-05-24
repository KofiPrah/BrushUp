"""
Fix SSL certificate issues for Django in Replit

This script disables SSL by creating empty certificate files 
and then starts the Django server in HTTP mode.
"""
import os
import sys
import subprocess
import signal

def main():
    # Print banner
    print("\n" + "=" * 70)
    print(" BRUSH UP - HTTP SERVER (SSL DISABLED) ".center(70, '='))
    print("=" * 70)
    
    # Create empty certificate files
    with open('cert.pem', 'w') as f:
        f.write('')
    with open('key.pem', 'w') as f:
        f.write('')
    
    print("Created empty certificate files to disable SSL")
    
    # Set environment variables
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
    os.environ['PYTHONUNBUFFERED'] = '1'
    os.environ['DJANGO_DEVELOPMENT'] = 'true'
    os.environ['DJANGO_DEBUG'] = 'true'
    
    # Run Django without SSL
    print("Starting Django in HTTP mode on port 5000")
    cmd = [sys.executable, 'manage.py', 'runserver', '0.0.0.0:5000']
    process = subprocess.Popen(cmd)
    
    # Handle SIGINT and SIGTERM
    def signal_handler(sig, frame):
        print("\nShutting down server...")
        process.terminate()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Wait for the process to complete
    process.wait()

if __name__ == "__main__":
    main()