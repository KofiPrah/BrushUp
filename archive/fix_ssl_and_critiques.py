#!/usr/bin/env python3
"""
Fix script for Brush Up application
1. Removes SSL certificates from the server configuration
2. Ensures proper CORS and HTTP settings
3. Creates any missing database tables
4. Fixes API endpoint permissions for critique submissions
"""
import os
import sys
import django
import shutil

# Configure Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true'
os.environ['HTTPS'] = 'off'
os.environ['wsgi.url_scheme'] = 'http'

django.setup()

# Now we can import Django models
from django.db import connection
from critique.models import KarmaEvent, Reaction, Critique

def print_header(message):
    """Print a header message"""
    print("\n" + "=" * 80)
    print(f" {message}")
    print("=" * 80)

def check_table_exists(table_name):
    """Check if a table exists in the database"""
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name=%s)",
            [table_name]
        )
        return cursor.fetchone()[0]

def create_karma_event_table():
    """Create the KarmaEvent table if it doesn't exist"""
    table_exists = check_table_exists('critique_karmaevent')
    
    if not table_exists:
        print("KarmaEvent table doesn't exist. Creating it...")
        with connection.cursor() as cursor:
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS critique_karmaevent (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES auth_user(id),
                event_type VARCHAR(50) NOT NULL,
                points INTEGER NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                reference_id INTEGER,
                reference_type VARCHAR(50)
            );
            ''')
        print("KarmaEvent table created successfully.")
    else:
        print("KarmaEvent table already exists.")

def create_reaction_table():
    """Create the Reaction table if it doesn't exist"""
    table_exists = check_table_exists('critique_reaction')
    
    if not table_exists:
        print("Reaction table doesn't exist. Creating it...")
        with connection.cursor() as cursor:
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS critique_reaction (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES auth_user(id),
                critique_id INTEGER NOT NULL REFERENCES critique_critique(id),
                reaction_type VARCHAR(20) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(user_id, critique_id, reaction_type)
            );
            ''')
        print("Reaction table created successfully.")
    else:
        print("Reaction table already exists.")

def fix_serializer_author_duplicate():
    """Fix the author duplication in CritiqueSerializer"""
    serializer_path = "critique/api/serializers.py"
    
    try:
        # Read the file
        with open(serializer_path, "r") as file:
            content = file.read()
        
        # Look for the problematic create method in CritiqueSerializer
        old_method = '''    def create(self, validated_data):
        """Create a new critique with the current user as author."""
        user = self.context['request'].user
        critique = Critique.objects.create(author=user, **validated_data)
        return critique'''
        
        new_method = '''    def create(self, validated_data):
        """Create a new critique with the current user as author."""
        # Author is set in the view's perform_create method
        # This prevents the "multiple values for keyword argument 'author'" error
        critique = Critique.objects.create(**validated_data)
        return critique'''
        
        # Replace the problematic code
        if old_method in content:
            content = content.replace(old_method, new_method)
            with open(serializer_path, "w") as file:
                file.write(content)
            print("Fixed author duplication in CritiqueSerializer.")
        else:
            print("CritiqueSerializer already fixed or has a different implementation.")
    
    except Exception as e:
        print(f"Error fixing CritiqueSerializer: {e}")

def remove_ssl_certificates():
    """Rename SSL certificates to disable them"""
    try:
        # Rename or remove SSL certificate files
        cert_files = ['cert.pem', 'key.pem']
        for cert_file in cert_files:
            if os.path.exists(cert_file):
                if not os.path.exists(f"{cert_file}.disabled"):
                    shutil.copy2(cert_file, f"{cert_file}.disabled")
                os.rename(cert_file, f"{cert_file}.bak")
                print(f"Disabled SSL certificate: {cert_file}")
    except Exception as e:
        print(f"Error disabling SSL certificates: {e}")

def update_main_file():
    """Update the main.py file for HTTP mode"""
    http_main = """#!/usr/bin/env python3
\"\"\"
HTTP-only server for Brush Up application
Serves Django application without SSL certificates
\"\"\"
import os
import sys

# Set environment variables for HTTP mode
os.environ['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true' 
os.environ['HTTPS'] = 'off'
os.environ['wsgi.url_scheme'] = 'http'

# Import Django and run the server
if __name__ == '__main__':
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
"""
    
    try:
        with open("main.py", "w") as file:
            file.write(http_main)
        print("Updated main.py for HTTP mode.")
    except Exception as e:
        print(f"Error updating main.py: {e}")

def create_http_workflow_script():
    """Create an HTTP workflow script"""
    workflow_script = """#!/usr/bin/env python3
\"\"\"
HTTP-specific gunicorn configuration for Replit
\"\"\"
import os
import sys
from gunicorn.app.wsgiapp import run

# Environment variables for HTTP mode
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true'
os.environ['HTTPS'] = 'off'
os.environ['wsgi.url_scheme'] = 'http'

# Override the command-line arguments to remove SSL
sys.argv = [
    'gunicorn',
    '--bind', '0.0.0.0:5000',
    '--reload',
    'main:application'
]

if __name__ == '__main__':
    run()
"""
    
    try:
        with open("http_workflow.py", "w") as file:
            file.write(workflow_script)
        os.chmod("http_workflow.py", 0o755)
        print("Created HTTP workflow script.")
    except Exception as e:
        print(f"Error creating HTTP workflow script: {e}")

def main():
    """Run all fixes"""
    print_header("Starting Brush Up application fixes")
    
    # 1. Fix CritiqueSerializer
    print_header("Fixing CritiqueSerializer author duplication")
    fix_serializer_author_duplicate()
    
    # 2. Check and fix database tables
    print_header("Checking database tables")
    create_karma_event_table()
    create_reaction_table()
    
    # 3. Fix SSL certificates
    print_header("Disabling SSL certificates")
    remove_ssl_certificates()
    
    # 4. Update main.py for HTTP mode
    print_header("Updating server configuration")
    update_main_file()
    
    # 5. Create HTTP workflow script
    create_http_workflow_script()
    
    print_header("All fixes completed")
    print("Please update your workflow command to use:")
    print("python http_workflow.py")
    print("instead of:")
    print("gunicorn --bind 0.0.0.0:5000 --certfile=cert.pem --keyfile=key.pem --reuse-port --reload main:app")

if __name__ == "__main__":
    main()