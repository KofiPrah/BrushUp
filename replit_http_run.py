"""
Replit-compatible HTTP server for Brush Up application
Disables SSL completely and runs Django in HTTP-only mode
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
    """Run Django in HTTP-only mode"""
    # Set environment variables for Django
    os.environ['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
    os.environ['PYTHONUNBUFFERED'] = '1'
    os.environ['DJANGO_DEVELOPMENT'] = 'true'
    os.environ['DJANGO_DEBUG'] = 'true'
    
    # Remove SSL certificates
    try:
        if os.path.exists('cert.pem'):
            os.remove('cert.pem')
        if os.path.exists('key.pem'):
            os.remove('key.pem')
    except Exception as e:
        print(f"Error removing SSL certificates: {e}")
    
    # Print banner
    print("\n" + "=" * 70)
    print(" BRUSH UP - HTTP MODE ".center(70, '='))
    print("=" * 70)
    print("Starting Django development server on port 5000")
    
    # Run Django development server
    cmd = [sys.executable, 'manage.py', 'runserver', '0.0.0.0:5000']
    env = os.environ.copy()
    
    try:
        subprocess.run(cmd, env=env)
    except Exception as e:
        print(f"Error running Django server: {e}")

if __name__ == "__main__":
    main()