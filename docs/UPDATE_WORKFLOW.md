# Updating the Art Critique Application Workflow

To fix SSL/HTTP compatibility issues with Replit's load balancer, follow these steps to update your workflow.

## Option 1: Update the Workflow in Replit UI

1. In the Replit interface, click on 'Tools' in the left sidebar
2. Select 'Workflows'
3. Edit the 'Start application' workflow
4. Change the command to:
   ```
   python run_in_http_mode.py
   ```
5. Click 'Save' to update the workflow

## Option 2: Run the Application Manually

You can also run the application manually with:

```
./run_http_only.sh
```

This script will:
- Set the necessary environment variables
- Kill any existing server processes
- Start Gunicorn in HTTP-only mode

## Technical Details

The HTTP-only mode is needed because Replit's load balancer handles SSL termination. This means:

1. External requests come to Replit over HTTPS
2. The load balancer decrypts these requests
3. The load balancer forwards plain HTTP requests to your application
4. Your application must be configured to accept HTTP, not HTTPS

If your application is configured to use SSL/HTTPS internally, it will reject the plain HTTP requests from the load balancer with an error like:

```
[SSL: HTTP_REQUEST] http request (_ssl.c:2580)
```

The `run_in_http_mode.py` and `run_http_only.sh` scripts fix this by:
- Setting the SSL_ENABLED environment variable to false
- Configuring Gunicorn to listen on HTTP instead of HTTPS
- Removing SSL certificate configuration (--certfile, --keyfile)