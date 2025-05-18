#!/bin/bash

# Start the server in HTTP mode without SSL certificates
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload http_fixed_server:app