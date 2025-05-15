# Art Critique App Deployment Guide

## Current Deployment Issue

The application is currently running in HTTPS mode with self-signed certificates, which causes browser security warnings as seen in the error message: "This site can't provide a secure connection".

## Deployment Options

### Option 1: Deploy with Replit Autoscale (Recommended)

Replit Autoscale provides automatic HTTPS support through Replit's infrastructure. This is the easiest and most secure option.

#### Key Requirements for Autoscale
1. Your app must bind to the `$PORT` that Replit provides (not a hard-coded port)
2. Your app must run in plain HTTP mode (Replit handles the HTTPS/TLS)
3. Your app must respond to HTTP requests with valid responses (200, 300, or even 404)

#### Step 1: Update Your `.replit` File
```toml
modules = ["python-3.11", "postgresql-16"]

[nix]
channel = "stable-24_05"
packages = ["openssl", "postgresql"]

[deployment]
deploymentTarget = "autoscale"
run = [
  "sh", "-c",                          
  "gunicorn -b 0.0.0.0:${PORT:-8080} artcritique.wsgi:application"
]

# No [[ports]] section needed - Replit injects $PORT automatically
```

#### Step 2: Test Your Configuration Locally
```bash
# In your Replit shell
export PORT=8080
gunicorn -b 0.0.0.0:$PORT artcritique.wsgi:application
```

Then in a second shell tab:
```bash
curl -v http://127.0.0.1:8080/
```

You should see valid HTTP headers. If not, troubleshoot your application startup.

#### Step 3: Deploy Your Application
1. Click the "Deploy" button in Replit
2. Immediately check the logs to verify startup
3. Look for "Listening at: http://0.0.0.0:$PORT" and "Booting worker with pid"
4. Your app will be accessible via a secure `.replit.app` domain

### Option 2: Continue Using Self-Signed Certificates (Development Only)

For development environments, you can continue using the self-signed certificates:

1. When accessing the application, you'll need to:
   - Click "Advanced" on the browser warning page
   - Click "Proceed to [site] (unsafe)"
   - Add a security exception in your browser
   
2. For Brave browser users specifically:
   - See instructions in BRAVE_BROWSER_NOTES.md
   - You may need to disable shields temporarily for this domain

### Option 3: Run in Plain HTTP Mode (Not Secure)

If you're just testing and don't need HTTPS:

1. Modify the workflow in `.replit` to use plain HTTP:
   - Remove the `--certfile` and `--keyfile` options 
   - Set `SSL_ENABLED = "false"` in the environment section

2. Use the provided `start_http.sh` script to run in HTTP mode:
   ```
   ./start_http.sh
   ```

## Troubleshooting

### Common Error: ERR_SSL_PROTOCOL_ERROR

If you get the error `ERR_SSL_PROTOCOL_ERROR` in your browser, this almost always means the Replit load-balancer could not complete an ordinary HTTP request to your container. This typically happens when:

1. No process is really listening on `$PORT`
2. The process crashes before the first byte is written

#### Troubleshooting Steps:

1. **Verify the service is running**:
   ```bash
   export PORT=8080
   gunicorn -b 0.0.0.0:$PORT artcritique.wsgi:application
   ```
   Confirm Gunicorn prints "Booting worker" and stays running.

2. **Check connectivity from inside the container**:
   ```bash
   curl -v http://127.0.0.1:8080/
   ```
   You should get valid HTTP headers back.

3. **Check for common issues**:
   - If you see `ModuleNotFoundError: main` → Correct the module path
   - If you see `Address already in use` → Choose a different port
   - If Gunicorn exits immediately → Check for missing dependencies

4. **Verify correct `.replit` settings**:
   - Make sure you're binding to `${PORT}`
   - Don't include `--certfile` or `--keyfile` options
   - Remove any `[[ports]]` section

5. **Add a health check endpoint** (optional):
   ```python
   # In your Django project/urls.py
   from django.http import JsonResponse
   urlpatterns += [
       path("healthz/", lambda r: JsonResponse({"ok": True})),
   ]
   ```
   
   Then add to your `.replit` file:
   ```toml
   [env]
   REPLIT_HEALTHCHECK_PATH = "/healthz/"
   ```

### Other Common Issues

* If you see "Invalid request: [SSL: HTTP_REQUEST]" in logs:
  - The client is sending HTTP requests to an HTTPS server
  - Either configure the client to use HTTPS or the server to use HTTP

* If the browser shows "This site can't provide a secure connection":
  - Your self-signed certificates aren't trusted by the browser
  - Use Option 1 (Autoscale) for a production deployment

### Last Resort Debugging

If you've tried everything and still can't get your app deployed:

1. **Cross-check with a dummy server**:
   Replace your run command in `.replit` with a trivial Python server:
   ```toml
   run = ["python", "-m", "http.server", "${PORT}"]
   ```
   
   Redeploy. If the dummy server loads, the infrastructure is fine and you can focus on your application code. If even the dummy server fails, the workspace itself might have issues.

2. **Check Django configuration**:
   Make sure `ALLOWED_HOSTS` in your Django settings includes:
   ```python
   ALLOWED_HOSTS = [
       '0.0.0.0',
       'localhost',
       '127.0.0.1',
       '.replit.app',  # Allow all replit.app subdomains
   ]
   ```

3. **Remember the TL;DR**:
   - Local curl inside the pod first
   - Bind exactly to `0.0.0.0:$PORT`, plain HTTP
   - Make sure the import path is correct (artcritique.wsgi:application)
   
   Fix those three and the ERR_SSL_PROTOCOL_ERROR should disappear every time.