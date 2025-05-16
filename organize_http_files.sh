#!/bin/bash
# Script to organize HTTP files into proper folders

# Create target directories if they don't exist
mkdir -p scripts/http scripts/s3 tests/http tests/s3

# Copy HTTP scripts to scripts/http (not moving to avoid breaking paths)
echo "Copying HTTP scripts to scripts/http directory..."
for file in run_http_*.sh start_*http*.sh *http_server*.py; do
  if [ -f "$file" ]; then
    cp "$file" scripts/http/
    echo "  - Copied $file"
  fi
done

# Copy S3 scripts to scripts/s3
echo "Copying S3 scripts to scripts/s3 directory..."
for file in test_s3_*.py *s3_*.py; do
  if [ -f "$file" ]; then
    cp "$file" scripts/s3/
    echo "  - Copied $file"
  fi
done

echo "Done organizing files."
