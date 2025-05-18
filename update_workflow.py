#!/usr/bin/env python3
"""
Update the workflow configuration to run the Django server in HTTP mode.
This script modifies the .replit file to update the run command.
"""
import os
import json

# Create a simpler HTTP version of main.py
with open("main.py.http", "w") as f:
    f.write("""#!/usr/bin/env python3
'''
HTTP-only Django app for Brush Up in Replit environment
'''
import os

# Configure Django for HTTP mode
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artcritique.settings")
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"
os.environ["HTTPS"] = "off"
os.environ["wsgi.url_scheme"] = "http"

# Import Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Create app variable for gunicorn
app = application
""")

# Make it executable
os.chmod("main.py.http", 0o755)

# Copy it to main.py
with open("main.py.http", "r") as src:
    with open("main.py", "w") as dst:
        dst.write(src.read())

print("Updated main.py for HTTP mode")

# Create a gunicorn config for HTTP mode
with open("gunicorn_http_config.py", "w") as f:
    f.write("""
bind = "0.0.0.0:5000"
workers = 1
reload = True
""")

print("Created gunicorn HTTP config")

# Update the workflow command
print("To start the server in HTTP mode, use the command:")
print("gunicorn --config=gunicorn_http_config.py main:app")
print("\nMake sure to update your workflow in Replit to use this command.")

print("\nAll done! The server should now run in HTTP mode without SSL certificates.")