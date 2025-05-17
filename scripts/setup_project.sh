#!/bin/bash
# Master script to set up the Art Critique project
# This includes organizing files and configuring the HTTP server

# Print a formatted header
print_header() {
  echo "======================================================"
  echo "  $1"
  echo "======================================================"
}

# Copy HTTP script to root for workflow
copy_http_script() {
  print_header "Setting up HTTP server script"
  cp scripts/http/start_http.sh ./
  chmod +x ./start_http.sh
  echo "✓ HTTP server script copied to root directory"
}

# Fix SSL issues
fix_ssl_issues() {
  print_header "Fixing SSL issues"
  python scripts/http/fix_ssl_issue.py
  echo "✓ SSL issues fixed"
}

# Main function
main() {
  print_header "Art Critique Project Setup"
  
  # Copy HTTP script to root
  copy_http_script
  
  # Fix SSL issues
  fix_ssl_issues
  
  print_header "Setup Complete"
  echo "To start the server in HTTP mode, run: ./start_http.sh"
  echo "To run tests, run: ./scripts/run_all_tests.sh"
}

# Run the main function
main
