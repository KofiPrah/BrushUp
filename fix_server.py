#!/usr/bin/env python
"""
Fix server configuration for Brush Up application
"""
import os
import shutil
import django

def fix_serializer():
    """Fix CritiqueSerializer by removing duplicate methods"""
    try:
        from fix_critique_serializer import add_missing_method
        add_missing_method()
        print("✓ Fixed CritiqueSerializer")
    except Exception as e:
        print(f"! Error fixing CritiqueSerializer: {str(e)}")

def create_dummy_certificates():
    """Create dummy SSL certificates if they don't exist"""
    # Create self-signed certificates
    if not os.path.exists('cert.pem') or not os.path.exists('key.pem'):
        print("Creating self-signed certificates...")
        os.system('openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 -subj "/CN=localhost" 2>/dev/null')
        print("✓ Created SSL certificates")

if __name__ == "__main__":
    fix_serializer()
    create_dummy_certificates()
    print("✓ Server configuration fixed. Please restart the workflow.")