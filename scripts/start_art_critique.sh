#!/bin/bash
# Main entry point for Art Critique application
# This script selects the best way to start the application based on the environment

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
  echo "  --http       Start server in HTTP mode (no SSL)"
  echo "  --help       Display this help message"
  echo ""
  echo "Available Utilities:"
  echo "  ./scripts/setup_project.sh    Set up the project environment"
  echo "  ./scripts/run_all_tests.sh    Run all tests"
  echo "  ./scripts/http/start_http.sh  Start in HTTP-only mode"
  echo ""
  echo "See PROJECT_OVERVIEW.md for more information"
}

# Start HTTP server
start_http_server() {
  print_header "Starting Art Critique in HTTP Mode"
  echo "This mode is compatible with Replit's load balancer"
  echo "Running scripts/http/start_http.sh..."
  
  # Run the HTTP server script
  exec scripts/http/start_http.sh
}

# Default action is to display usage
if [ $# -eq 0 ]; then
  display_usage
  echo -e "\nStarting in HTTP mode by default...\n"
  start_http_server
  exit 0
fi

# Parse command line arguments
for arg in "$@"; do
  case $arg in
    --http)
      start_http_server
      exit 0
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