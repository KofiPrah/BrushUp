#!/usr/bin/env python3
"""
HTTP-only server for Brush Up application
Runs Django in HTTP mode (no SSL) to work with Replit environment
"""
import os
import subprocess

def main():
    """
    Run the Django application in HTTP mode (no SSL certificates)
    """
    # Fix the CritiqueSerializer issue
    try:
        from fix_critique_serializer import add_missing_method
        add_missing_method()
        print("✓ Successfully fixed CritiqueSerializer")
    except Exception as e:
        print(f"! Error fixing serializer: {str(e)}")

    # Run using gunicorn for production (HTTP mode, no SSL)
    cmd = ["gunicorn", "--bind", "0.0.0.0:5000", "--reuse-port", "--reload", "wsgi:application"]
    subprocess.run(cmd)

if __name__ == "__main__":
    main()