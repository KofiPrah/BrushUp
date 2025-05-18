#!/usr/bin/env python
"""
HTTP-only server for Brush Up application

This script runs the Django server directly using the development server,
completely bypassing the SSL configuration issues.
"""
import os
import sys
import django
import inspect
from pathlib import Path

# Ensure we're using the correct Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artcritique.settings")
django.setup()

# Fix missing method in CritiqueSerializer if needed
from critique.api.serializers import CritiqueSerializer

def add_missing_method():
    """Add missing get_reactions_count method to CritiqueSerializer if needed"""
    if not hasattr(CritiqueSerializer, 'get_reactions_count'):
        # Define the method
        def get_reactions_count(self, obj):
            """Return the total count of all reactions for this critique."""
            return obj.reactions.count()
        
        # Add the method to the class
        setattr(CritiqueSerializer, 'get_reactions_count', get_reactions_count)
        print("✓ Added missing get_reactions_count method to CritiqueSerializer")
    else:
        print("✓ CritiqueSerializer already has get_reactions_count method")

# Run the method to fix the serializer
add_missing_method()

# Now run the Django server directly
if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    
    print("\n===== Starting Brush Up in HTTP-only mode =====\n")
    
    # Run the development server
    execute_from_command_line(["manage.py", "runserver", "0.0.0.0:8000"])