# Deployment Configuration for Art Critique

## Current Deployment Configuration

The application is configured for deployment using Replit's Autoscale feature. Here's the minimal configuration for the `.replit` file:

```
modules = ["python-3.11", "postgresql-16"]

[nix]
channel  = "stable-24_05"
packages = ["openssl", "postgresql"]

[deployment]
deploymentTarget = "autoscale"
run = [
  "sh", "-c",                          # ➜ use a shell so $PORT expands
  "gunicorn -b 0.0.0.0:${PORT:-8080} main:app"
]

# No [[ports]] section needed in Autoscale – Replit injects $PORT
```

## Deployment Notes

1. The application binds to the `$PORT` environment variable that Replit provides at runtime
2. No ports block is needed with Autoscale, Replit handles the routing automatically
3. SSL/HTTPS is handled by Replit's infrastructure
4. The application runs in HTTP mode internally

## Manual Setup Instructions

If needed, you can manually run the server with:

```bash
./run.sh
```

The script automatically uses the PORT environment variable or defaults to port 5000 if not defined.

## Deployment Logs

When deploying, watch the deployment logs. Once you see "Starting server on port $PORT" followed by Gunicorn's "Listening at" message, the application is ready to accept connections.