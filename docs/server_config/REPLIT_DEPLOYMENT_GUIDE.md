# Replit Deployment Guide for Art Critique

This guide provides instructions for deploying the Art Critique Django application on Replit's Autoscale platform.

## Understanding Local Development vs. Deployment

There are two modes of operation for this application:

1. **Local Development** (with HTTPS):
   - Uses self-signed certificates stored in `certs/cert.pem` and `certs/key.pem`
   - Handles TLS termination in the application
   - Binds to port 5000

2. **Replit Deployment** (plain HTTP):
   - No SSL certificates needed (Replit handles TLS termination)
   - Uses the PORT environment variable set by Replit
   - Simple HTTP binding

## Deployment Configuration

To deploy this application on Replit Autoscale, you need to create a proper `.replit` configuration file:

```toml
[deployment]
deploymentTarget = "autoscale"
run = [
  "sh", "-c",
  "gunicorn -b 0.0.0.0:${PORT:-8080} artcritique.wsgi:application"
]

[env]
REPLIT_HEALTHCHECK_PATH = "/api/health/"
SSL_ENABLED = "false"
```

## Important Notes

1. **Do not use SSL/TLS in the Gunicorn command**
   - Replit's load balancer already handles TLS termination, so your app should run over plain HTTP
   - Remove any `--certfile` and `--keyfile` parameters from your Gunicorn command

2. **Always bind to `0.0.0.0:$PORT`**
   - Replit Autoscale sets the `PORT` environment variable to a random high number
   - Your application must listen on that port to be accessible

3. **Add a health check endpoint**
   - The application already includes a health check endpoint at `/api/health/`
   - This is important for Replit to verify that your application is running correctly

## Troubleshooting Deployment Issues

If you encounter an `ERR_SSL_PROTOCOL_ERROR` when deploying:

1. **Verify local functionality**
   ```bash
   export PORT=8080  # Choose any free port
   python scripts/cli.py serve --protocol http   # Use the unified CLI
   ```

2. **Test the HTTP endpoint locally**
   ```bash
   curl -v http://127.0.0.1:8080/api/health/
   ```

3. **Check your deployment logs**
   - After deploying, immediately click on the "Logs" button to see any startup errors

## Complete Deployment Process

1. Create the appropriate `.replit` file (as shown above)
2. Commit your changes
3. Click "Deploy → Autoscale"
4. View the logs to ensure the application starts correctly
5. Once deployed, your app will be available under a `.replit.app` domain

## Database Considerations

- The application is configured to use the PostgreSQL database credentials from environment variables
- Make sure the production database is properly configured and accessible from the deployment environment