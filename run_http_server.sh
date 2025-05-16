#!/bin/bash
# Start Gunicorn with plain HTTP (no SSL)

export SSL_ENABLED=false
exec gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app