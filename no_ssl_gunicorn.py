"""
Simple script to run Django without SSL in Replit
This script removes the SSL certificates and runs gunicorn without SSL
"""
import os
import sys
import signal
import subprocess

def signal_handler(sig, frame):
    """Handle termination signals gracefully"""
    print("\nShutting down server...")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def main():
    """Run gunicorn in HTTP-only mode"""
    # Create empty files instead of using --certfile and --keyfile
    with open('cert.pem', 'w') as f:
        f.write('')
    with open('key.pem', 'w') as f:
        f.write('')
    
    # Set environment variables
    os.environ['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
    os.environ['PYTHONUNBUFFERED'] = '1'
    os.environ['SSL_ENABLED'] = 'false'
    os.environ['HTTP_ONLY'] = 'true'
    
    # Print banner
    print("\n" + "=" * 70)
    print(" BRUSH UP - HTTP MODE ".center(70, '='))
    print("=" * 70)
    print("Starting gunicorn server in HTTP-only mode on port 5000")
    
    # Run Django with gunicorn but without SSL flags
    cmd = ['gunicorn', '--bind', '0.0.0.0:5000', '--reuse-port', '--reload', 'main:app']
    subprocess.run(cmd)

if __name__ == "__main__":
    main()