# How to Fix the SSL/HTTP Issue

## Problem
The application is currently configured to use SSL certificates (HTTPS), but
Replit's load balancer already handles SSL termination before requests reach
our application. This causes "Invalid request: HTTP_REQUEST" errors.

## Solution
You need to reconfigure the Replit workflow to use HTTP mode:

1. Open the `.replit` file in the Replit editor
2. Find this section:
   ```
   [[workflows.workflow.tasks]]
   task = "shell.exec"
   args = "gunicorn --bind 0.0.0.0:5000 --certfile=cert.pem --keyfile=key.pem --reuse-port --reload main:app"
   waitForPort = 5000
   ```

3. Change it to:
   ```
   [[workflows.workflow.tasks]]
   task = "shell.exec"
   args = "./start_http.sh"
   waitForPort = 5000
   ```

4. Save the file and restart the workflow

## Alternative: Run HTTP Server Manually
If you can't edit the `.replit` file, you can run the HTTP server manually:

1. Stop the current workflow
2. In the Shell, run:
   ```
   ./start_http.sh
   ```

## Files Created by This Script
- `start_http.sh`: Script to start the HTTP server
- `replit_http.sh`: Symbolic link for workflow use
- `main.py`: Updated to force HTTP mode
- `main.py.original`: Backup of the original main.py (if created)

