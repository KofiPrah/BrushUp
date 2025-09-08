# Art Critique HTTP Configuration

## Fixing SSL/HTTP Compatibility Issues

I've updated your application to work with bucket ownership enforcement for S3 and to run in HTTP-only mode with Replit's load balancer. 

## Current Issue

Your application is still trying to use HTTPS internally, causing errors:
```
Invalid request from ip=127.0.0.1: [SSL: HTTP_REQUEST] http request (_ssl.c:2580)
```

## How to Fix

### Option 1: Update Workflow (Recommended)

1. Click on **Tools** in the left sidebar
2. Select **Workflows**
3. Edit the **Start application** workflow
4. Change the command to:
   ```
   ./scripts/run_http_only.sh
   ```
5. Click Save

### Option 2: Run Manually

You can also run the application manually with:
```
./scripts/run_http_only.sh
```

## Technical Details

The HTTP-only configuration:
- Sets SSL_ENABLED to false
- Configures Gunicorn to listen on HTTP instead of HTTPS
- Prevents Gunicorn from using SSL certificates
- Works properly with Replit's load balancer

## S3 Storage Updates

I've also updated the S3 storage configuration to work with bucket ownership enforcement:
- No ACLs are used (they're disabled with ownership enforcement)
- Bucket policies are used for access control instead
- The storage classes handle ownership correctly

You'll need to set up your bucket policy to allow public read access to the media folder. See `docs/S3_WITH_BUCKET_OWNERSHIP.md` for details.