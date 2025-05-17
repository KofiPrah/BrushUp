#!/bin/bash
# Main server script for Art Critique application
# This script delegates to the implementation in scripts/http/run_server.sh

exec scripts/http/run_server.sh "$@"
