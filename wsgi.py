"""
WSGI configuration for Brush Up application
"""
import os
import django

# Configure Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
django.setup()

# Apply serializer fixes
try:
    # Fix the reactions_set issue in CritiqueSerializer
    from critique.api.serializers import CritiqueSerializer
    # Check if any instance method uses reaction_set
    serializer_path = 'critique/api/serializers.py'
    with open(serializer_path, 'r') as file:
        content = file.read()
    if 'obj.reaction_set' in content:
        content = content.replace('obj.reaction_set', 'obj.reactions')
        with open(serializer_path, 'w') as file:
            file.write(content)
        print("✓ Fixed reaction_set references in CritiqueSerializer")
except Exception as e:
    print(f"! Error fixing serializer: {str(e)}")

# Get Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()