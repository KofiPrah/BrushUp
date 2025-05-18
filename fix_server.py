#!/usr/bin/env python3
"""
Fix the server configuration issues by running a simple HTTP server
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true'
os.environ['HTTPS'] = 'off'
os.environ['wsgi.url_scheme'] = 'http'

# Initialize Django
django.setup()

# Make sure CritiqueSerializer has the necessary methods
try:
    from critique.api.serializers import CritiqueSerializer
    
    def ensure_reaction_methods():
        """Fix the CritiqueSerializer to have proper reaction methods"""
        if not hasattr(CritiqueSerializer, 'get_reactions_count'):
            def get_reactions_count(self, obj):
                """Return the total count of all reactions for this critique."""
                return {
                    'HELPFUL': obj.reactions.filter(reaction_type='HELPFUL').count(),
                    'INSPIRING': obj.reactions.filter(reaction_type='INSPIRING').count(),
                    'DETAILED': obj.reactions.filter(reaction_type='DETAILED').count(),
                    'TOTAL': obj.reactions.count()
                }
            CritiqueSerializer.get_reactions_count = get_reactions_count
            print("✓ Added get_reactions_count method to CritiqueSerializer")
    
    ensure_reaction_methods()
except Exception as e:
    print(f"Warning: Could not fix serializer: {e}")

if __name__ == "__main__":
    print("\n=== Starting Brush Up in HTTP mode (no SSL) ===\n")
    
    # Run the Django development server without SSL
    sys.argv = ['manage.py', 'runserver', '0.0.0.0:8000']
    execute_from_command_line(sys.argv)