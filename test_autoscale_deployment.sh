#!/bin/bash
# Script to test Autoscale deployment locally

# Verify proper import paths
python -c "import artcritique.wsgi" 2>/dev/null
if [ $? -ne 0 ]; then
  echo "ERROR: Cannot import artcritique.wsgi - check module paths"
  exit 1
else
  echo "✓ Import paths verified"
fi

# Kill any existing processes using port 8080
echo "Checking for existing processes on port 8080..."
lsof -i:8080 -t | xargs kill -9 2>/dev/null

# Test with Autoscale-like environment
echo "Starting test server with \$PORT=8080..."
export PORT=8080
export SSL_ENABLED=false

# Try to start Gunicorn with correct settings
gunicorn -b 0.0.0.0:$PORT artcritique.wsgi:application &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Check if process is still running
if kill -0 $SERVER_PID 2>/dev/null; then
  echo "✓ Server started successfully (PID: $SERVER_PID)"
else
  echo "ERROR: Server failed to start"
  exit 1
fi

# Try to connect to verify HTTP response
echo "Testing HTTP connection..."
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8080/ > /tmp/http_code
HTTP_CODE=$(cat /tmp/http_code)

if [[ $HTTP_CODE == 2* ]] || [[ $HTTP_CODE == 3* ]] || [[ $HTTP_CODE == 404 ]]; then
  echo "✓ HTTP connection successful (Status: $HTTP_CODE)"
else
  echo "ERROR: HTTP connection failed (Status: $HTTP_CODE)"
  echo "Try running: curl -v http://127.0.0.1:8080/ for details"
fi

# Check that allowed hosts includes replit.app
echo "Checking Django ALLOWED_HOSTS setting..."
python -c "from artcritique.settings import ALLOWED_HOSTS; print('.replit.app' in ' '.join(ALLOWED_HOSTS) or any(h.endswith('.replit.app') for h in ALLOWED_HOSTS))" 2>/dev/null | grep -q "True"
if [ $? -eq 0 ]; then
  echo "✓ ALLOWED_HOSTS includes .replit.app domain"
else
  echo "WARNING: ALLOWED_HOSTS may not include .replit.app"
  echo "Consider adding '.replit.app' to ALLOWED_HOSTS in settings.py"
fi

# Clean up
echo "Cleaning up test server..."
kill $SERVER_PID

echo -e "\nAutoscale deployment test complete"
echo "If all checks passed, you're ready to deploy to Autoscale!"
echo "Update your .replit file as described in DEPLOYMENT_GUIDE.md"