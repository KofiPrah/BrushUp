# HTTP Server Configuration for Replit

This guide explains how to configure the Art Critique application to work with Replit's load balancer using HTTP mode.

## Background

Replit's load balancer handles SSL termination, which means:

1. HTTPS connections from users go to Replit's load balancer
2. The load balancer decrypts the traffic
3. The load balancer forwards plain HTTP traffic to our application

This creates a conflict if our application tries to use HTTPS (SSL/TLS) internally, leading to the error:
```
Invalid request from ip=127.0.0.1: [SSL: HTTP_REQUEST] http request (_ssl.c:2580)
```

## Solution: HTTP-only Mode

To solve this issue, we need to run our application in HTTP-only mode. This repository includes several scripts that configure the application correctly:

### Option 1: Use http_only_server.py

This script starts the application with Gunicorn in HTTP mode:

```bash
python http_only_server.py
```

It sets the necessary environment variables:
- `SSL_ENABLED=false`
- `SECURE_SSL_REDIRECT=false`

And configures Gunicorn without SSL certificates.

### Option 2: Use restart_http_server.sh

This script stops any existing server processes and starts the application in HTTP mode:

```bash
./restart_http_server.sh
```

### Option 3: Use the unified CLI

This replaces the previous `run_http_only.py` helper:

```bash
python scripts/cli.py serve --protocol http
```

## S3 Storage in HTTP Mode

To use S3 storage with HTTP mode:

1. Start the application with both HTTP mode and S3 enabled:

```bash
USE_S3=True SSL_ENABLED=false python http_only_server.py
```

2. Ensure your S3 bucket has the correct permissions by running:

```bash
python update_bucket_policy.py
```

This updates the bucket policy to allow public access without using ACLs.

## Troubleshooting

### HTTP/HTTPS Issues

If you see SSL/HTTPS errors in the logs:

1. Check if Gunicorn is started with SSL certificates
2. Verify that `SSL_ENABLED` and `SECURE_SSL_REDIRECT` are set to `false`
3. Make sure the server is listening on port 5000

### S3 Access Issues

If images aren't loading from S3:

1. Run the test script to verify S3 connectivity:

```bash
python test_s3_connection.py
```

2. Check if your bucket has Block Public Access settings enabled:

```bash
python diagnose_s3_permissions.py
```

3. Update the bucket policy to allow public access:

```bash
python update_bucket_policy.py
```

## Workflow Configuration

The default workflow for the application is configured to use Gunicorn with HTTP mode:

```
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

You can modify this in the Replit workflow settings if needed.