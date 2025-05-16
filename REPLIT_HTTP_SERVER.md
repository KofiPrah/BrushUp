# Running Art Critique on Replit: HTTP Mode

This document explains how to run the Art Critique application on Replit in HTTP mode. This is necessary because Replit's load balancer handles SSL termination, which means our application should run in plain HTTP mode internally.

## The Problem

When running on Replit, we encounter the following error:

```
[SSL: HTTP_REQUEST] http request (_ssl.c:2580)
```

This happens because:
1. Gunicorn is configured to use HTTPS (with SSL certificates)
2. But Replit's load balancer sends plain HTTP requests
3. This mismatch causes the SSL error

## Solutions

We've provided several methods to run the application in HTTP mode:

### Option 1: Use the HTTP-only Shell Script

This is the simplest method:

```bash
./start_http_server.sh
```

This script:
- Sets environment variables to disable SSL
- Starts Gunicorn without SSL certificates

### Option 2: Use Gunicorn with Config File

We've created a Gunicorn config file specifically for HTTP mode:

```bash
./start_with_http_config.sh
```

This uses the `gunicorn_http_config.py` configuration file, which explicitly disables SSL.

### Option 3: Run Python Script

For a more programmatic approach, use the Python script:

```bash
python run_http_only.py
```

### Option 4: Use HTTP Server Wrapper

There's also a Python module that wraps the Django application:

```bash
python http_server.py
```

## Documentation of Files

- `gunicorn_http_config.py` - Gunicorn configuration for HTTP mode
- `start_http_server.sh` - Bash script to start in HTTP mode
- `start_with_http_config.sh` - Bash script using the config file
- `run_http_only.py` - Python script for HTTP mode
- `replit_server.py` - Comprehensive server with HTTP mode
- `http_server.py` - Simple HTTP server wrapper

## How to Check If It's Working

When the server starts correctly, you should see:

```
Running in HTTP mode (SSL handled by Replit's load balancer)
```

And you should NOT see the following error:

```
[SSL: HTTP_REQUEST] http request (_ssl.c:2580)
```

## Troubleshooting

If you're still seeing SSL errors:

1. Make sure there are no active processes using port 5000
2. Check that SSL is disabled in Django settings (`SSL_ENABLED = False`)
3. Try restarting the Replit environment
4. Ensure that `certfile` and `keyfile` parameters are not being passed to Gunicorn