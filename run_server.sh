#!/bin/bash

# Run the server with SSL support
exec gunicorn --bind 0.0.0.0:5000 --certfile=cert.pem --keyfile=key.pem --reuse-port --reload artcritique.wsgi:application