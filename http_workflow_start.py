#!/usr/bin/env python3
"""
HTTP-only workflow starter for Brush Up application in Replit

This script handles starting the application in HTTP mode without requiring
SSL certificates, and adds the missing get_reactions_count method to 
CritiqueSerializer to fix the AttributeError.
"""
import os
import subprocess
import sys
import django

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')

# Force HTTP mode
os.environ['HTTPS'] = 'off'
os.environ['HTTP_ONLY'] = 'true'
os.environ['SSL_ENABLED'] = 'false'
os.environ['wsgi.url_scheme'] = 'http'

# Initialize Django
django.setup()

# Fix the CritiqueSerializer missing methods
try:
    from critique.api.serializers import CritiqueSerializer
    
    # Define the missing get_reactions_count method
    def get_reactions_count(self, obj):
        """Return the total count of all reactions for this critique."""
        return obj.reactions.count()
    
    # Add missing method to the serializer
    if not hasattr(CritiqueSerializer, 'get_reactions_count'):
        setattr(CritiqueSerializer, 'get_reactions_count', get_reactions_count)
        print("✓ Added missing get_reactions_count method to CritiqueSerializer")
except Exception as e:
    print(f"Warning: Error fixing CritiqueSerializer: {e}")

# Start the HTTP server
print("Starting HTTP server (no SSL certificates)...")
cmd = [
    "gunicorn",
    "--bind", "0.0.0.0:5000",
    "--reload",
    "main:app"
]

# Launch the server
os.execvp(cmd[0], cmd)