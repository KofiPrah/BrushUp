"""
Simple standalone server for Brush Up application
"""
import os
import sys
import django

# Configure environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')

# Apply serializer fix first
try:
    django.setup()
    from fix_critique_serializer import add_missing_method
    add_missing_method()
    print("✓ Added missing get_reactions_count method to CritiqueSerializer")
except Exception as e:
    print(f"! Error fixing serializer: {str(e)}")

# Run the standard Django development server
if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line([sys.argv[0], "runserver", "0.0.0.0:5000"])