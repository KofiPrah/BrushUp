#!/bin/bash
# Apply fixes to S3 bucket and objects to ensure they have correct permissions

# Enable set -e to exit on error
set -e

# Print banner
echo "==============================================" 
echo "  Art Critique S3 Permission Fix Tool"
echo "=============================================="
echo ""

# Run diagnostic first to see current state
echo "Running S3 diagnostics..."
python diagnose_s3_permissions.py

# Confirm with user
echo ""
echo "This script will apply the following fixes:"
echo "1. Update bucket policy to allow public access"
echo "2. Apply public-read ACL to all existing artwork uploads" 
echo ""
read -p "Do you want to continue? (y/n): " confirm

if [ "$confirm" != "y" ]; then
  echo "Operation cancelled."
  exit 0
fi

# Run the fix script
echo ""
echo "Applying fixes..."
python fix_s3_permissions.py

# Run diagnostics again to verify
echo ""
echo "Verifying fixes..."
python diagnose_s3_permissions.py

echo ""
echo "S3 permission fixes complete."
echo "You may need to restart the application with './start_with_s3.sh'"