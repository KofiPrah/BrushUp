# S3 Fix Scripts

These scripts help fix issues with AWS S3 storage integration.

## Scripts

- `fix_one_image.py`: Fix accessibility for a single image in S3
- `fix_s3_permissions.py`: Fix permissions for S3 objects
- `apply_s3_fixes.sh`: Apply all S3 fixes in sequence

## Usage

```bash
# Fix permissions for a specific image
python scripts/fixes/s3/fix_one_image.py

# Fix permissions for all S3 objects
python scripts/fixes/s3/fix_s3_permissions.py

# Apply all S3 fixes
bash scripts/fixes/s3/apply_s3_fixes.sh
```
