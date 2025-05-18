"""
HTTP-only server for Brush Up application
This script runs Django in HTTP mode without SSL certificates
"""
import os
import sys
import subprocess
import socket
import time
import logging
import signal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def print_banner(message):
    """Print a formatted banner message"""
    line = "-" * len(message)
    logger.info("\n%s\n%s\n%s", line, message, line)

def is_port_in_use(port):
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def signal_handler(sig, frame):
    """Handle termination signals"""
    print_banner("Shutting down server...")
    if 'process' in globals():
        process.terminate()
    sys.exit(0)

def run_django_server():
    """Run Django server directly without SSL"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Kill any process that might be using port 8000
    if is_port_in_use(8000):
        print_banner("Port 8000 is already in use. Attempting to free it...")
        try:
            subprocess.run(['pkill', '-f', 'runserver'], check=False)
            time.sleep(1)
        except Exception as e:
            logger.error("Error killing existing process: %s", e)
    
    # Run Django in HTTP mode
    print_banner("Starting Django server in HTTP mode")
    
    # Set environment variables to disable SSL
    env = os.environ.copy()
    env['SSL_ENABLED'] = 'false'
    
    # Use Python's runserver directly (no SSL)
    cmd = [
        sys.executable,
        'manage.py',
        'runserver',
        '0.0.0.0:8000',
    ]
    
    global process
    process = subprocess.Popen(cmd, env=env)
    
    try:
        process.wait()
    except KeyboardInterrupt:
        print_banner("Keyboard interrupt received")
        process.terminate()
        process.wait()
        print_banner("Server stopped")

if __name__ == "__main__":
    print_banner("Running Brush Up in HTTP-only mode")
    run_django_server()