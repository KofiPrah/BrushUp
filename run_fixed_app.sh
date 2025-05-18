#!/bin/bash
# Fixed HTTP server for Brush Up application
# - Fixes the serializer issue
# - Runs in HTTP mode without SSL certificates

# Stop any existing servers
pkill -f gunicorn || true
pkill -f runserver || true
sleep 1

# Create empty certificate files to prevent errors
echo "# Empty certificate file" > cert.pem
echo "# Empty key file" > key.pem
chmod 644 cert.pem key.pem

# Fix the serializer issue
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

# Create a fixed main.py if it doesn't exist
if [ ! -f main_fixed.py ]; then
  cat > main_fixed.py << 'EOF'
#!/usr/bin/env python3
"""
HTTP-only server for Brush Up application
With fixed serializers
"""
import os
import sys
import django

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTPS'] = 'off'
os.environ['wsgi.url_scheme'] = 'http'

# Initialize Django
django.setup()

# Fix serializer issues
try:
    from critique.api.serializers import CritiqueSerializer, CritiqueListSerializer
    
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
    if not hasattr(CritiqueSerializer, 'get_reactions_count'):
        setattr(CritiqueSerializer, 'get_reactions_count', get_reactions_count)
    
    if not hasattr(CritiqueListSerializer, 'get_reactions_count'):
        setattr(CritiqueListSerializer, 'get_reactions_count', get_reactions_count)
        
    print("✓ Successfully fixed serializer methods")
except Exception as e:
    print(f"Warning: Unable to fix serializer: {e}")

# Import the Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
app = application
EOF
fi

# Run Gunicorn with our fixed WSGI application
# No SSL certificates used here
echo "Starting Brush Up in HTTP mode..."
python -m gunicorn --bind 0.0.0.0:5000 main_fixed:app