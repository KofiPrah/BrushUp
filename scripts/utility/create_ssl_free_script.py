#!/usr/bin/env python3
"""
Create a simple script that runs without SSL certificates, to use in the workflow
"""

with open("start_http_mode.py", "w") as file:
    file.write("""#!/usr/bin/env python3
\"\"\"
HTTP-only server starter that doesn't require SSL certificates
\"\"\"
import os
import sys
import subprocess

# Set environment variables for HTTP mode
os.environ['DJANGO_SETTINGS_MODULE'] = 'artcritique.settings'
os.environ['SSL_ENABLED'] = 'false'
os.environ['HTTP_ONLY'] = 'true' 
os.environ['HTTPS'] = 'off'
os.environ['wsgi.url_scheme'] = 'http'

# Run Django directly through manage.py to avoid gunicorn's SSL requirements
cmd = [sys.executable, "manage.py", "runserver", "0.0.0.0:5000"]
print(f"Starting server with command: {' '.join(cmd)}")
subprocess.run(cmd)
""")

# Make it executable
import os
os.chmod("start_http_mode.py", 0o755)

print("Created start_http_mode.py - a simple starter script without SSL requirements")
print("Use it in your workflow with: python start_http_mode.py")