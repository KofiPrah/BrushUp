#!/bin/bash

# Run the server with plain HTTP (for Replit deployment)
exec gunicorn --bind 0.0.0.0:${PORT:-5000} --reuse-port --reload artcritique.wsgi:application