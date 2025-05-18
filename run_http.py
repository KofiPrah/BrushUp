#!/usr/bin/env python
"""
HTTP Server for Brush Up

This script runs Django directly with gunicorn in HTTP-only mode,
avoiding SSL certificate requirements.
"""
import os
import sys
import subprocess
from pathlib import Path

def print_header(message):
    """Print a formatted header message"""
    print("\n" + "=" * 80)
    print(f" {message} ".center(80, "="))
    print("=" * 80 + "\n")

def main():
    """Run the Django application in HTTP mode with gunicorn"""
    print_header("Starting Brush Up in HTTP Mode")

    # Create empty certificate files if they don't exist
    # This ensures the workflow can find them even though we won't use them
    for cert_file in ['cert.pem', 'key.pem']:
        if not Path(cert_file).exists():
            print(f"Creating empty {cert_file} file")
            Path(cert_file).touch()

    # Start gunicorn with explicit HTTP configuration
    cmd = [
        "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--reload",
        "artcritique.wsgi:application"
    ]
    
    print("Starting server with command:", " ".join(cmd))
    subprocess.run(cmd)

if __name__ == "__main__":
    main()