#!/usr/bin/env python
"""
Start both the main Django application and the media server in separate processes.
"""
import os
import subprocess
import sys
import time
import signal

# Process handles
main_process = None
media_process = None

def signal_handler(sig, frame):
    """Handle termination signals cleanly."""
    print("Shutting down servers...")
    if media_process:
        media_process.terminate()
    if main_process:
        main_process.terminate()
    sys.exit(0)

def main():
    """Start the Django application and media server."""
    global main_process, media_process
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start the media server
        print("Starting media server...")
        media_process = subprocess.Popen(
            [sys.executable, "serve_media.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give the media server a moment to start
        time.sleep(1)
        
        # Check if media server started successfully
        if media_process.poll() is not None:
            out, err = media_process.communicate()
            print(f"Error starting media server: {err}")
            return 1
            
        print("Media server started successfully.")
        
        # Start the main Django application with gunicorn
        print("Starting main application...")
        main_process = subprocess.Popen(
            ["gunicorn", "--bind", "0.0.0.0:5000", "--certfile=cert.pem", 
             "--keyfile=key.pem", "--reuse-port", "--reload", "main:app"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("Main application started successfully.")
        print("Services are running. Press Ctrl+C to stop.")
        
        # Keep the script running and monitor subprocesses
        while True:
            # Check if either process has terminated
            if main_process.poll() is not None:
                out, err = main_process.communicate()
                print(f"Main application exited: {err}")
                media_process.terminate()
                return 1
                
            if media_process.poll() is not None:
                out, err = media_process.communicate()
                print(f"Media server exited: {err}")
                main_process.terminate()
                return 1
                
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Interrupted by user.")
        return signal_handler(signal.SIGINT, None)
    except Exception as e:
        print(f"Error: {e}")
        # Clean up any running processes
        if media_process and media_process.poll() is None:
            media_process.terminate()
        if main_process and main_process.poll() is None:
            main_process.terminate()
        return 1

if __name__ == "__main__":
    sys.exit(main())