#!/usr/bin/env python3
"""
HTTP-only server for Brush Up application that works in Replit
With fixed get_reactions_count method in serializers
"""
import os
import sys
import django

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTPS'] = 'off'
os.environ['HTTP_ONLY'] = 'true'
os.environ['wsgi.url_scheme'] = 'http'

# Initialize Django
django.setup()

# Fix serializer issues
try:
    from critique.api.serializers import CritiqueSerializer, CritiqueListSerializer
    
    # Check if the method already exists in the serializers
    serializer_fixed = hasattr(CritiqueSerializer, 'get_reactions_count')
    list_serializer_fixed = hasattr(CritiqueListSerializer, 'get_reactions_count')
    
    # Define the missing method
    def get_reactions_count(self, obj):
        """Return the total count of all reactions for this critique."""
        return {
            'HELPFUL': obj.reactions.filter(reaction_type='HELPFUL').count(),
            'INSPIRING': obj.reactions.filter(reaction_type='INSPIRING').count(),
            'DETAILED': obj.reactions.filter(reaction_type='DETAILED').count(),
            'TOTAL': obj.reactions.count()
        }
    
    # Add the method to both serializers if needed
    if not serializer_fixed:
        setattr(CritiqueSerializer, 'get_reactions_count', get_reactions_count)
        print("✓ Added get_reactions_count to CritiqueSerializer")
    
    if not list_serializer_fixed:
        setattr(CritiqueListSerializer, 'get_reactions_count', get_reactions_count)
        print("✓ Added get_reactions_count to CritiqueListSerializer")
    
    print("✓ Successfully fixed serializer methods")
except Exception as e:
    print(f"Warning: Unable to fix serializer: {e}")

# Import the Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
app = application