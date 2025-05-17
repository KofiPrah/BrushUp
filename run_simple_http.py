import os

# Set environment variables for HTTP-only mode
os.environ["SSL_ENABLED"] = "false"
os.environ["HTTP_ONLY"] = "true"

# Import Django WSGI application
from artcritique.wsgi import application

# Set variable for Gunicorn
app = application

# Print confirmation
print("Server set up for HTTP mode (no SSL)")
