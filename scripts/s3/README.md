# S3 Storage Scripts

This directory contains scripts for working with AWS S3 storage in the Art Critique application.

## Directory Structure

- `fix/`: Scripts for fixing S3 storage issues
  - `diagnose_s3_permissions.py`: Diagnose S3 permissions issues
  - `final_s3_fix.py`: Apply final S3 fixes
  - `fix_s3_permissions.py`: Fix S3 permissions

- `tests/`: Tests for S3 functionality
  - `test_django_s3_upload.py`: Test Django S3 upload
  - `test_s3_browser.py`: Test S3 browser
  - `test_s3_connection.py`: Test S3 connection
  - `test_s3_upload_utility.py`: Test S3 upload utility

- `utils/`: Utility scripts for S3
  - `s3_deep_debug.py`: Comprehensive diagnostic tool
  - `setup_s3_env.sh`: Set up S3 environment variables

- `verification/`: Scripts to verify S3 configuration
  - `verify_new_s3_config.py`: Verify new S3 configuration
  - `verify_s3_connection.py`: Verify S3 connection
  - `verify_s3_integration.py`: Verify S3 integration

## Usage

These scripts can be run directly from the command line:

```bash
# Run diagnostics
python scripts/s3/utils/s3_deep_debug.py

# Fix permissions
python scripts/s3/fix/fix_s3_permissions.py

# Verify connection
python scripts/s3/verification/verify_s3_connection.py

# Set up environment
bash scripts/s3/utils/setup_s3_env.sh
```

Or use the main test runner:

```bash
./scripts/run_app --test=s3
```
