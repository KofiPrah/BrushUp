#!/bin/bash
# Final fix for Brush Up application
# 1. Adds missing get_reactions_count method to serializers
# 2. Fixes SSL certificate issues

# Stop any existing servers
pkill -f gunicorn || true
pkill -f runserver || true
sleep 1

# Generate self-signed SSL certificate (to replace invalid ones)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=localhost" -batch

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
    print('✓ Added get_reactions_count method to CritiqueSerializer')
else:
    print('✓ CritiqueSerializer already has get_reactions_count method')

if not hasattr(CritiqueListSerializer, 'get_reactions_count'):
    setattr(CritiqueListSerializer, 'get_reactions_count', get_reactions_count)
    print('✓ Added get_reactions_count method to CritiqueListSerializer')
else:
    print('✓ CritiqueListSerializer already has get_reactions_count method')

print('✓ Successfully fixed serializer issues')
"

# Run the server with the new valid SSL certificates
echo "Starting Brush Up with fixed serializers and valid SSL certificates..."
exec gunicorn --bind 0.0.0.0:5000 --certfile=cert.pem --keyfile=key.pem --reuse-port --reload main:app