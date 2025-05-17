#!/bin/bash
# Run all tests for the Art Critique application
# This script will run all the test categories in sequence

set -e  # Exit immediately if a command fails

print_header() {
  echo "======================================================"
  echo "$1"
  echo "======================================================"
}

# HTTP Tests
run_http_tests() {
  print_header "Running HTTP Server Tests"
  python tests/http/test_http_server.py --url http://localhost:5000
  python tests/http/test_http_workflow.py --skip-remote
}

# API Tests
run_api_tests() {
  print_header "Running API Tests"
  python tests/api/test_notification_api.py
  python tests/api/test_api_auth.py --url http://localhost:5000
  python tests/api/test_notifications.py
}

# Authentication Tests
run_auth_tests() {
  print_header "Running Authentication Tests"
  python tests/auth/test_auth_api.py
  python tests/auth/test_auth_image_upload.py
}

# S3 Tests
run_s3_tests() {
  print_header "Running S3 Storage Tests"
  python scripts/s3/tests/test_s3_connection.py
  python scripts/s3/verification/verify_s3_integration.py --skip-upload
  python scripts/s3/tests/test_s3_browser.py --skip-browser
  python scripts/s3/tests/test_django_s3_upload.py --skip-upload
  python scripts/s3/tests/test_s3_upload_utility.py --skip-upload
}

# Media Tests
run_media_tests() {
  print_header "Running Media Tests"
  python tests/media/test_image_upload.py --skip-upload
  python tests/media/test_image_display.py --skip-display
  python tests/media/test_new_upload.py --skip-upload
}

# Frontend Tests
run_frontend_tests() {
  print_header "Running Frontend Tests"
  python tests/frontend/test_karma.py --skip-browser
}

# Deployment Tests
run_deployment_tests() {
  print_header "Running Deployment Tests"
  echo "Running deployment tests is skipped in test mode"
  # These tests are typically run in a separate CI/CD environment
  # bash tests/deployment/test_autoscale_deployment.sh
}

# Run all tests
print_header "Art Critique Test Suite"
echo "Starting tests at $(date)"
echo ""

# Parse command line arguments
RUN_HTTP=true
RUN_API=true
RUN_AUTH=true
RUN_S3=true
RUN_MEDIA=true
RUN_FRONTEND=true
RUN_DEPLOYMENT=false  # Disabled by default

# Process arguments
for arg in "$@"; do
  case $arg in
    --no-http)
      RUN_HTTP=false
      ;;
    --no-api)
      RUN_API=false
      ;;
    --no-auth)
      RUN_AUTH=false
      ;;
    --no-s3)
      RUN_S3=false
      ;;
    --no-media)
      RUN_MEDIA=false
      ;;
    --no-frontend)
      RUN_FRONTEND=false
      ;;
    --with-deployment)
      RUN_DEPLOYMENT=true
      ;;
    --http-only)
      RUN_API=false
      RUN_AUTH=false
      RUN_S3=false
      RUN_MEDIA=false
      RUN_FRONTEND=false
      RUN_DEPLOYMENT=false
      ;;
    --api-only)
      RUN_HTTP=false
      RUN_AUTH=false
      RUN_S3=false
      RUN_MEDIA=false
      RUN_FRONTEND=false
      RUN_DEPLOYMENT=false
      ;;
    --auth-only)
      RUN_HTTP=false
      RUN_API=false
      RUN_S3=false
      RUN_MEDIA=false
      RUN_FRONTEND=false
      RUN_DEPLOYMENT=false
      ;;
    --s3-only)
      RUN_HTTP=false
      RUN_API=false
      RUN_AUTH=false
      RUN_MEDIA=false
      RUN_FRONTEND=false
      RUN_DEPLOYMENT=false
      ;;
    --media-only)
      RUN_HTTP=false
      RUN_API=false
      RUN_AUTH=false
      RUN_S3=false
      RUN_FRONTEND=false
      RUN_DEPLOYMENT=false
      ;;
    --frontend-only)
      RUN_HTTP=false
      RUN_API=false
      RUN_AUTH=false
      RUN_S3=false
      RUN_MEDIA=false
      RUN_DEPLOYMENT=false
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --no-http          Skip HTTP tests"
      echo "  --no-api           Skip API tests"
      echo "  --no-auth          Skip authentication tests"
      echo "  --no-s3            Skip S3 storage tests"
      echo "  --no-media         Skip media tests"
      echo "  --no-frontend      Skip frontend tests"
      echo "  --with-deployment  Include deployment tests"
      echo "  --http-only        Run only HTTP tests"
      echo "  --api-only         Run only API tests"
      echo "  --auth-only        Run only authentication tests"
      echo "  --s3-only          Run only S3 storage tests"
      echo "  --media-only       Run only media tests"
      echo "  --frontend-only    Run only frontend tests"
      echo "  --help             Display this help message"
      exit 0
      ;;
  esac
done

# Run the tests according to the flags
if $RUN_HTTP; then
  run_http_tests
fi

if $RUN_API; then
  run_api_tests
fi

if $RUN_AUTH; then
  run_auth_tests
fi

if $RUN_S3; then
  run_s3_tests
fi

if $RUN_MEDIA; then
  run_media_tests
fi

if $RUN_FRONTEND; then
  run_frontend_tests
fi

if $RUN_DEPLOYMENT; then
  run_deployment_tests
fi

print_header "Test Suite Complete"
echo "Tests completed at $(date)"
