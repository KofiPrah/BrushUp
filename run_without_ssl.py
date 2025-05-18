#!/usr/bin/env python3
"""
Script to run Django in HTTP mode without SSL certificates
"""
import os
import subprocess
import signal
import sys

def signal_handler(sig, frame):
    """Handle termination signals"""
    print("\nShutting down...")
    sys.exit(0)

def main():
    """Run the Django application in HTTP-only mode"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Set environment variables
    os.environ['SSL_ENABLED'] = 'false'
    os.environ['HTTP_ONLY'] = 'true'
    os.environ['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
    os.environ['HTTPS'] = 'off'
    os.environ['wsgi.url_scheme'] = 'http'
    
    print("Starting Brush Up in HTTP-only mode...")
    command = ["gunicorn", "--bind", "0.0.0.0:5000", "--reuse-port", "--reload", "main:app"]
    
    try:
        process = subprocess.Popen(command)
        process.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error running server: {e}")
    finally:
        if 'process' in locals() and process:
            process.terminate()

if __name__ == "__main__":
    main()