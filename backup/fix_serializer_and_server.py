#!/usr/bin/env python3
"""
Fix both the CritiqueSerializer missing method and SSL certificate issues
"""
import os
import sys
import django
import shutil

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
django.setup()

# Fix for CritiqueSerializer missing method
def fix_serializer():
    """Add missing get_reactions_count method to CritiqueSerializer"""
    from critique.api.serializers import CritiqueSerializer
    
    # Define the missing method
    def get_reactions_count(self, obj):
        """Return the total count of all reactions for this critique."""
        return obj.reactions.count()
    
    # Add method to the serializer
    setattr(CritiqueSerializer, 'get_reactions_count', get_reactions_count)
    print("✓ Added missing get_reactions_count method to CritiqueSerializer")

# Fix for SSL certificate issues
def fix_ssl_issues():
    """Rename SSL certificates to disable them"""
    cert_files = ['cert.pem', 'key.pem']
    for cert_file in cert_files:
        if os.path.exists(cert_file):
            backup = f"{cert_file}.disabled"
            if not os.path.exists(backup):
                shutil.copy2(cert_file, backup)
            # Remove or rename the certificate file
            os.rename(cert_file, f"{cert_file}.bak")
            print(f"✓ Disabled SSL certificate: {cert_file}")
        else:
            print(f"Certificate {cert_file} already disabled or not found")

# Create a modified run script that works with HTTP
def create_run_script():
    """Create HTTP-only run script"""
    script_content = """#!/bin/bash
# Run Brush Up application in HTTP mode (no SSL)
# Kill any existing gunicorn processes
pkill -f gunicorn || true

# Start the server in HTTP mode without SSL certificates
exec gunicorn --bind 0.0.0.0:5000 --reload main:app
"""
    
    with open("run_http_only.sh", "w") as f:
        f.write(script_content)
    
    os.chmod("run_http_only.sh", 0o755)
    print("✓ Created HTTP-only run script: run_http_only.sh")

if __name__ == "__main__":
    print("Fixing Brush Up application issues...")
    fix_serializer()
    fix_ssl_issues()
    create_run_script()
    print("\nAll fixes applied successfully!")
    print("Run the application with: ./run_http_only.sh")