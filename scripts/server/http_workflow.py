#!/usr/bin/env python3
"""
HTTP-only workflow script for Brush Up application
"""
import os
import sys
import django
from django.core.wsgi import get_wsgi_application

# Set environment variables for HTTP mode
os.environ['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true'
os.environ['HTTPS'] = 'off'
os.environ['wsgi.url_scheme'] = 'http'

# Create empty certificate files
for filename in ['cert.pem', 'key.pem']:
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            f.write("")

# Initialize Django
django.setup()

# Apply the serializer fixes
from critique.api.serializers import CritiqueSerializer, CritiqueListSerializer

def get_reactions_count(self, obj):
    """Return the total count of all reactions for this critique."""
    return {
        'HELPFUL': obj.reactions.filter(reaction_type='HELPFUL').count(),
        'INSPIRING': obj.reactions.filter(reaction_type='INSPIRING').count(),
        'DETAILED': obj.reactions.filter(reaction_type='DETAILED').count(),
        'TOTAL': obj.reactions.count()
    }

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

# Apply the methods to both serializer classes
for cls in [CritiqueSerializer, CritiqueListSerializer]:
    cls.get_reactions_count = get_reactions_count
    cls.get_helpful_count = get_helpful_count
    cls.get_inspiring_count = get_inspiring_count
    cls.get_detailed_count = get_detailed_count
    cls.get_user_reactions = get_user_reactions

print("✓ Successfully fixed CritiqueSerializer methods")

# Create the application
application = get_wsgi_application()
app = application