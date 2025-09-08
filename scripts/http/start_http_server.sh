#!/bin/bash
# HTTP-only server for Brush Up application
# This script:
# 1. Stops any existing servers
# 2. Fixes the CritiqueSerializer to add the missing get_reactions_count method
# 3. Runs the application in HTTP mode (without SSL certificates)

# Kill any existing server processes
echo "Stopping any existing servers..."
pkill -f gunicorn || true
pkill -f runserver || true
sleep 1

# Set environment variables for HTTP mode
export SSL_ENABLED=false
export HTTPS=off
export HTTP_ONLY=true
export wsgi_url_scheme=http

# Fix the CritiqueSerializer issue
echo "Applying serializer fixes..."
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

# Add method to both serializers if needed
if not hasattr(CritiqueSerializer, 'get_reactions_count'):
    setattr(CritiqueSerializer, 'get_reactions_count', get_reactions_count)
    print('✓ Added get_reactions_count to CritiqueSerializer')
else:
    print('✓ CritiqueSerializer already has get_reactions_count method')

if not hasattr(CritiqueListSerializer, 'get_reactions_count'):
    setattr(CritiqueListSerializer, 'get_reactions_count', get_reactions_count)
    print('✓ Added get_reactions_count to CritiqueListSerializer')
else:
    print('✓ CritiqueListSerializer already has get_reactions_count method')

print('✓ Serializer fixes applied successfully')
"

# Run the server in HTTP mode (no SSL certificates)
echo "Starting Brush Up in HTTP mode..."
exec gunicorn --bind 0.0.0.0:5000 main:app
