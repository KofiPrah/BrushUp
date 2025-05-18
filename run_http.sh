#!/bin/bash
export SSL_ENABLED=false
export HTTP_ONLY=true
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
