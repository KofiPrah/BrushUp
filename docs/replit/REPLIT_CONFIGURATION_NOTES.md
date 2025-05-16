# Replit Configuration Notes

For Autoscale deployment, simplify your `.replit` file as follows:

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

## Key Points
- Bind to the $PORT environment variable provided by Replit
- Run in plain HTTP mode (Replit handles SSL/HTTPS)
- No ports mapping needed for Autoscale deployments
   - Let Replit's infrastructure handle HTTPS automatically

4. Remove any duplicate workflows running Gunicorn with SSL certificates.

5. Checking Deployment:
   - Watch the deployment logs to confirm the server has started
   - Once the listener is up, Replit's public URL should load without the "couldn't reach" message
   - The application will be accessible via the Replit URL