"""
Simple server for Brush Up application
Uses the original configuration that was working with brushup.replit.app
"""
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
django.setup()

# Apply the fix for CritiqueSerializer
try:
    from fix_critique_serializer import add_missing_method
    add_missing_method()
    print("✓ Successfully fixed CritiqueSerializer's get_reactions_count method")
except Exception as e:
    print(f"! Error fixing CritiqueSerializer: {str(e)}")

# Run Django directly using the development server
if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line(["manage.py", "runserver", "0.0.0.0:5000"])