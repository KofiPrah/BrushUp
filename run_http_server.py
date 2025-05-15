import os
import subprocess
import sys

# Simple script to run the application in HTTP mode
if __name__ == "__main__":
    # Set environment variable to disable SSL
    os.environ["SSL_ENABLED"] = "false"
    
    # Define the port to use
    port = int(os.environ.get("PORT", 8080))
    
    # Print information
    print(f"Starting server in HTTP mode on port {port}")
    print("This server can be used for testing the image upload functionality")
    print("Press Ctrl+C to stop the server")
    
    # Construct the command to run
    cmd = [
        "gunicorn",
        "--bind", f"0.0.0.0:{port}",
        "--reuse-port",
        "--reload",
        "main:app"
    ]
    
    try:
        # Execute the command
        process = subprocess.run(cmd)
        sys.exit(process.returncode)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        sys.exit(0)