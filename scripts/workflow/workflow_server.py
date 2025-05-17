import os
import subprocess
import signal
import sys

def signal_handler(sig, frame):
    print('Shutting down server...')
    sys.exit(0)

def main():
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Set environment variables for plain HTTP mode
    os.environ['SSL_ENABLED'] = 'false'
    
    # Get port from environment variable or default to 5000
    port = os.environ.get('PORT', '5000')
    
    # Start the server in plain HTTP mode
    print(f"Starting server in plain HTTP mode on port {port}...")
    server_process = subprocess.Popen([
        "gunicorn",
        "--bind", f"0.0.0.0:{port}",
        "--reuse-port",
        "--reload",
        "main:app"
    ])
    
    # Keep the script running while the subprocess runs
    server_process.wait()

if __name__ == "__main__":
    main()