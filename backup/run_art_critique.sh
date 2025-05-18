#!/bin/bash
# Main entry point for running Art Critique application
# This script is the primary interface for starting the server

# Display banner
cat << "EOF"
  _____         _     _____        _  _    _                    
 |  _  |___ ___| |_  |     |___ _| ||_|  | |_ _ ___ ___ ___ ___ 
 |     |  _|  _|  _| |   --| . | . || |  |  _| | . | -_|  _|_ -|
 |__|__|_| |___|_|   |_____|___|___||_|  |_| |_|_  |___|_| |___|
                                             |___|              
EOF

# Help text
usage() {
  echo "Art Critique Application"
  echo "------------------------"
  echo "Usage: $0 [options]"
  echo
  echo "Options:"
  echo "  --http          Start with HTTP mode (default, recommended for Replit)"
  echo "  --https         Start with HTTPS mode (not recommended with Replit)"
  echo "  --with-s3       Enable S3 storage (requires AWS credentials)"
  echo "  --test          Run tests instead of starting the server"
  echo "  --test=category Run tests for a specific category"
  echo "                  (http|api|auth|s3|media|frontend)"
  echo "  --help          Display this help message"
  echo
  echo "Examples:"
  echo "  $0                   # Start in HTTP mode"
  echo "  $0 --with-s3         # Start with S3 storage enabled"
  echo "  $0 --test            # Run all tests"
  echo "  $0 --test=http       # Run HTTP tests only"
}

# Default options
USE_HTTP=true
USE_S3=false
RUN_TESTS=false
TEST_CATEGORY=""

# Parse command line arguments
for arg in "$@"; do
  case $arg in
    --http)
      USE_HTTP=true
      shift
      ;;
    --https)
      USE_HTTP=false
      shift
      ;;
    --with-s3)
      USE_S3=true
      shift
      ;;
    --test)
      RUN_TESTS=true
      shift
      ;;
    --test=*)
      RUN_TESTS=true
      TEST_CATEGORY="${arg#*=}"
      shift
      ;;
    --help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $arg"
      usage
      exit 1
      ;;
  esac
done

# Execute the appropriate script based on options
if [ "$RUN_TESTS" = true ]; then
  # Run tests
  echo "Running tests..."
  
  if [ -n "$TEST_CATEGORY" ]; then
    exec scripts/run_all_tests.sh "--${TEST_CATEGORY}-only"
  else
    exec scripts/run_all_tests.sh
  fi
else
  # Start the server
  SERVER_ARGS=""
  
  if [ "$USE_HTTP" = false ]; then
    SERVER_ARGS="$SERVER_ARGS --no-http"
  fi
  
  if [ "$USE_S3" = true ]; then
    SERVER_ARGS="$SERVER_ARGS --with-s3"
  fi
  
  exec scripts/http/run_server.sh $SERVER_ARGS
fi