# HTTP Fix Scripts

These scripts help fix issues with HTTP/HTTPS configuration.

## Scripts

- `fix_ssl_issue.py`: Fix SSL issues with Replit's load balancer
- `fix_http_server.py`: Run Gunicorn in HTTP mode without SSL
- `fix_server_ssl.py`: Configure the server for HTTP-only mode and patch serializer methods

## Usage

```bash
# Fix SSL issues
python scripts/fixes/http/fix_ssl_issue.py

# Start an HTTP-only server for local testing
python scripts/fixes/http/fix_http_server.py

# Configure server for HTTP-only mode and patch serializers
python scripts/fixes/http/fix_server_ssl.py
```
