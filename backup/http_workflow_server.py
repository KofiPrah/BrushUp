#!/usr/bin/env python3
"""
HTTP-only server for Brush Up application for use in workflow
"""
import os
import sys
import django
from django.core.wsgi import get_wsgi_application

# Set environment variables to force HTTP mode
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
os.environ['HTTPS'] = 'off'
os.environ['wsgi.url_scheme'] = 'http'
os.environ['HTTP_ONLY'] = 'true'
os.environ['SSL_ENABLED'] = 'false'

# Initialize Django
django.setup()

# Fix the CritiqueSerializer to use 'reactions' instead of 'reaction_set'
try:
    from critique.api.serializers import CritiqueSerializer
    
    # Define fixed methods
    def get_helpful_count(self, obj):
        """Return the count of HELPFUL reactions for this critique."""
        return obj.reactions.filter(reaction_type='HELPFUL').count()
        
    def get_inspiring_count(self, obj):
        """Return the count of INSPIRING reactions for this critique."""
        return obj.reactions.filter(reaction_type='INSPIRING').count()
        
    def get_detailed_count(self, obj):
        """Return the count of DETAILED reactions for this critique."""
        return obj.reactions.filter(reaction_type='DETAILED').count()
    
    def get_user_reactions(self, obj):
        """Return the user's reactions to this critique."""
        user = self.context.get('request').user
        if not user or user.is_anonymous:
            return []
        
        reactions = obj.reactions.filter(user=user)
        return [r.reaction_type for r in reactions]
    
    # Replace the methods
    CritiqueSerializer.get_helpful_count = get_helpful_count
    CritiqueSerializer.get_inspiring_count = get_inspiring_count
    CritiqueSerializer.get_detailed_count = get_detailed_count
    CritiqueSerializer.get_user_reactions = get_user_reactions
    
    print("✓ Successfully fixed CritiqueSerializer methods")
except Exception as e:
    print(f"Warning: Unable to fix serializer: {e}")

# Get the Django WSGI application
application = get_wsgi_application()

# Alias for gunicorn
app = application