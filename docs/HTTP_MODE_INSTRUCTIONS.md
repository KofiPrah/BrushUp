# HTTP Mode for Replit

This document explains how to run the Art Critique application in HTTP-only mode, which is required for proper operation with Replit's load balancer.

## Why HTTP Mode?

Replit's load balancer handles SSL termination before requests reach our application. When our application also tries to use SSL, this causes "Invalid request: HTTP_REQUEST" errors because the load balancer has already decrypted the HTTPS request.

## How to Use HTTP Mode

1. Run the application with the HTTP-only script:

```bash
./start_http_server.sh
```

This script:
- Sets environment variables to disable SSL
- Starts Gunicorn with HTTP settings
- Uses a special entry point (http_main.py)

## Files for HTTP Mode

- `http_main.py` - Entry point that loads HTTP settings
- `http_server_settings.py` - HTTP configuration module
- `start_http_server.sh` - Script to start the server in HTTP mode

## Updating the Workflow

To permanently update the Replit workflow to use HTTP mode:

1. Open the `.replit` file in the Replit editor
2. Change the command in the workflow from:
   ```
   gunicorn --bind 0.0.0.0:5000 --certfile=cert.pem --keyfile=key.pem --reuse-port --reload main:app
   ```
   to:
   ```
   ./start_http_server.sh
   ```

3. Set the `SSL_ENABLED` environment variable to `false`

## Troubleshooting

If you see errors like:

```
Invalid request from ip=127.0.0.1: [SSL: HTTP_REQUEST] http request (_ssl.c:2580)
```

This means the server is still trying to use SSL but receiving HTTP requests. Ensure you're using the HTTP mode scripts.