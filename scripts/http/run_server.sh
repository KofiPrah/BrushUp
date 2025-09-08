#!/bin/bash
# Unified server script that can start the application in different modes

# Default configuration
USE_HTTP=true
USE_S3=false

# Print header
print_header() {
  echo -e "\n======================================================"
  echo "  $1"
  echo "======================================================\n"
}

# Display usage information
display_usage() {
  print_header "Art Critique Server"
  echo "Usage: $0 [OPTION]"
  echo ""
  echo "Options:"
  echo "  --no-http    Start with HTTPS (not recommended with Replit)"
  echo "  --with-s3    Enable S3 storage (requires AWS credentials)"
  echo "  --help       Display this help message"
  echo ""
}

# Parse command line arguments
for arg in "$@"; do
  case $arg in
    --no-http)
      USE_HTTP=false
      shift
      ;;
    --with-s3)
      USE_S3=true
      shift
      ;;
    --help)
      display_usage
      exit 0
      ;;
    *)
      echo "Unknown option: $arg"
      display_usage
      exit 1
      ;;
  esac
done

# Configure environment
if [ "$USE_HTTP" = true ]; then
  export SSL_ENABLED=false
  export HTTP_ONLY=true
  print_header "Starting in HTTP mode (SSL handled by Replit's load balancer)"
else
  export SSL_ENABLED=true
  export HTTP_ONLY=false
  print_header "Starting in HTTPS mode with local SSL termination"
fi

# Configure S3
if [ "$USE_S3" = true ]; then
  export USE_S3=True
  echo "S3 storage enabled"
else
  export USE_S3=False
  echo "Local storage enabled"
fi

# Start the server
if [ "$USE_HTTP" = true ]; then
  # Run Gunicorn without SSL certificates
  echo "Starting Gunicorn without SSL certificates..."
  exec gunicorn --bind 0.0.0.0:5000 --workers=1 --threads=2 --reload main:app
else
  # Run Gunicorn with SSL certificates
  echo "Starting Gunicorn with SSL certificates..."
  exec gunicorn --bind 0.0.0.0:5000 --certfile=certs/cert.pem --keyfile=certs/key.pem --workers=1 --threads=2 --reload main:app
fi
