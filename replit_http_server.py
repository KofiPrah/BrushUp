#!/usr/bin/env python3
"""
HTTP-only WSGI application for Brush Up in Replit
"""
import os
import sys

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')

# Set HTTP-only environment variables
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true'
os.environ['HTTPS'] = 'off'
os.environ['wsgi.url_scheme'] = 'http'

# Initialize Django
import django
django.setup()

# Fix the CritiqueSerializer to use 'reactions' instead of 'reaction_set'
from critique.api.serializers import CritiqueSerializer

# Define corrected methods
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
setattr(CritiqueSerializer, 'get_helpful_count', get_helpful_count)
setattr(CritiqueSerializer, 'get_inspiring_count', get_inspiring_count)
setattr(CritiqueSerializer, 'get_detailed_count', get_detailed_count)
setattr(CritiqueSerializer, 'get_user_reactions', get_user_reactions)

print("✓ Fixed CritiqueSerializer to use reactions instead of reaction_set")

# Get the Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Alias for gunicorn
app = application