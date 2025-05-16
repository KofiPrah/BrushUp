#!/bin/bash
# Main entry point script for Art Critique application
# This script selects the proper startup method based on environment

# Set environment variables for S3 if needed
if [ -n "$USE_S3" ] && [ "$USE_S3" = "True" ]; then
  echo "Starting Art Critique with S3 storage enabled..."
  
  # Check if S3 environment variables are set
  if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ] || [ -z "$AWS_STORAGE_BUCKET_NAME" ]; then
    echo "Error: S3 storage is enabled but AWS credentials are missing."
    echo "Please make sure AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY and AWS_STORAGE_BUCKET_NAME are set."
    exit 1
  fi
  
  # Start with S3 configuration
  exec ./scripts/http/start_in_http_mode.sh
else
  echo "Starting Art Critique with local storage..."
  # Start with local storage
  exec ./scripts/http/start_in_http_mode.sh
fi