"""
Simple launcher script to run the Art Critique application in HTTP mode.
This ensures compatibility with Replit's environment.
"""
import os
import sys
import subprocess

# Set environment variables for HTTP mode
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"

def main():
    """Run the server in HTTP mode"""
    print("Starting Art Critique in HTTP mode")
    print("==================================")
    
    # Build the gunicorn command
    cmd = [
        "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--reuse-port",
        "--reload",
        "main:app"
    ]
    
    # Run the server
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nServer stopped")
    except Exception as e:
        print(f"Error starting server: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())