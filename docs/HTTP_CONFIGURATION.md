# HTTP Configuration for Replit

## Overview

This document explains the HTTP configuration for the Art Critique application running on Replit. Replit's load balancer handles SSL termination, which means external requests come to the application over HTTPS, but the load balancer forwards them as plain HTTP requests to the application.

## Why HTTP Mode is Needed

When running on Replit, we need to configure the application to use HTTP instead of HTTPS internally because:

1. Replit's load balancer handles SSL termination
2. The load balancer forwards plain HTTP requests to the application
3. If the application tries to use HTTPS internally, it will reject these plain HTTP requests with errors like:
   ```
   Invalid request from ip=127.0.0.1: [SSL: HTTP_REQUEST] http request (_ssl.c:2580)
   ```

## Configuration Changes

The following changes have been made to support HTTP mode:

1. **Environment Variables**: 
   - `SSL_ENABLED=false`
   - `SECURE_SSL_REDIRECT=false`

2. **Server Configuration**:
   - Gunicorn is configured to run without SSL certificates
   - The server listens on `http://0.0.0.0:5000` instead of `https://0.0.0.0:5000`

3. **Startup Scripts**:
   - `start_in_http_mode.sh`: Starts the server in HTTP mode
   - A symlink `start` points to this script for convenience

## How to Run in HTTP Mode

### Method 1: Using the Startup Script

```bash
./start_in_http_mode.sh
```

### Method 2: Updating the Workflow (Recommended)

1. In the Replit UI, click on **Tools** in the left sidebar
2. Select **Workflows**
3. Edit the **Start application** workflow
4. Change the command to:
   ```
   ./start_in_http_mode.sh
   ```
5. Click **Save**

## Verifying HTTP Mode

When the server is running in HTTP mode, you should see this line in the logs:

```
Listening at: http://0.0.0.0:5000
```

Note the `http://` protocol instead of `https://`. This confirms that the server is running in HTTP mode.

## Troubleshooting

If you see errors like this:

```
Invalid request from ip=127.0.0.1: [SSL: HTTP_REQUEST] http request (_ssl.c:2580)
```

It means the server is still trying to use HTTPS. Make sure you're using the HTTP-only startup script and that the environment variables are set correctly.