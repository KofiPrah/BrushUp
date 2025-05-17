#!/bin/bash

# Run the server with HTTP support for development
exec gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app