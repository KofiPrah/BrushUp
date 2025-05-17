# Fix Scripts

This directory contains scripts for fixing various issues in the Art Critique application.

## S3 Fixes

Scripts for fixing S3 storage issues:

- `fix_one_image.py`: Fix accessibility for a single image in S3
- `fix_s3_permissions.py`: Fix permissions for S3 objects
- `apply_s3_fixes.sh`: Apply all S3 fixes in sequence

## HTTP Fixes

Scripts for fixing HTTP/HTTPS configuration issues:

- `fix_ssl_issue.py`: Fix SSL issues with Replit's load balancer

## Usage

### S3 Fixes

```bash
# Fix permissions for a specific image
python scripts/fixes/s3/fix_one_image.py

# Fix permissions for all S3 objects
python scripts/fixes/s3/fix_s3_permissions.py

# Apply all S3 fixes
bash scripts/fixes/s3/apply_s3_fixes.sh
```

### HTTP Fixes

```bash
# Fix SSL issues with Replit's load balancer
python scripts/fixes/http/fix_ssl_issue.py
```
