#!/usr/bin/env python
"""
Fix SSL certificate issues for Django in Replit

This script disables SSL by creating empty certificate files 
and then starts the Django server in HTTP mode.
"""
import os
import subprocess
from pathlib import Path

def main():
    print("Creating dummy SSL certificates...")
    # Create empty certificate files
    Path("cert.pem").write_text("")
    Path("key.pem").write_text("")
    
    print("Disabling SSL in main.py...")
    # Create a simplified HTTP-only server
    with open("main.py", "w") as f:
        f.write("""#!/usr/bin/env python
import os
import django
from django.core.management import execute_from_command_line

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artcritique.settings")
django.setup()

# Add necessary fixes to serializers
from critique.api.serializers import CritiqueSerializer

# Add missing method if it doesn't already exist
if not hasattr(CritiqueSerializer, 'get_reactions_count'):
    def get_reactions_count(self, obj):
        \"\"\"Return the total count of all reactions for this critique.\"\"\"
        return obj.reactions.count()
    
    setattr(CritiqueSerializer, 'get_reactions_count', get_reactions_count)
    print("✓ Added missing get_reactions_count method to CritiqueSerializer")

if __name__ == "__main__":
    # Run server
    execute_from_command_line(["manage.py", "runserver", "0.0.0.0:5000"])
""")
    
    print("Setup complete. Run 'python main.py' to start the server in HTTP mode.")

if __name__ == "__main__":
    main()