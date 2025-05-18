#!/bin/bash

# Start the Django application without SSL certificates for HTTP mode
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app