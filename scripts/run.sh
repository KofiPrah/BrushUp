#!/bin/bash
# Legacy wrapper to start the application in HTTP mode
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/run_http.sh"
