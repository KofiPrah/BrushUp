#!/bin/bash
# Run Brush Up application without SSL certificates
# Replit handles HTTPS for us, so we don't need certificates

# Kill any existing Gunicorn processes
pkill -f gunicorn || true

# Apply serializer fixes
python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
django.setup()

from critique.api.serializers import CritiqueSerializer, CritiqueListSerializer

# Define the missing method
def get_reactions_count(self, obj):
    return {
        'HELPFUL': obj.reactions.filter(reaction_type='HELPFUL').count(),
        'INSPIRING': obj.reactions.filter(reaction_type='INSPIRING').count(),
        'DETAILED': obj.reactions.filter(reaction_type='DETAILED').count(),
        'TOTAL': obj.reactions.count()
    }

# Add the method to both serializers
if not hasattr(CritiqueSerializer, 'get_reactions_count'):
    setattr(CritiqueSerializer, 'get_reactions_count', get_reactions_count)
    print('✓ Added get_reactions_count to CritiqueSerializer')

if not hasattr(CritiqueListSerializer, 'get_reactions_count'):
    setattr(CritiqueListSerializer, 'get_reactions_count', get_reactions_count)
    print('✓ Added get_reactions_count to CritiqueListSerializer')

print('✓ Successfully fixed serializer methods')
"

# Start Gunicorn WITHOUT SSL certificates
exec gunicorn --bind 0.0.0.0:5000 main:app