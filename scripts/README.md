# Art Critique Scripts

This directory contains scripts for running, managing, and fixing the Art Critique application.

## Categories

### HTTP Scripts (`scripts/http/`)
Scripts for HTTP server configuration and management:
- `run_server.sh`: Main script to run the HTTP server
- `start_http.sh`: Simple HTTP start script
- `start_http_server.sh`: Start server in HTTP mode
- `config/`: HTTP server configuration files
- `modules/`: HTTP Python modules
- `runners/`: HTTP server runner implementations

### S3 Scripts (`scripts/s3/`)
Scripts for AWS S3 storage configuration, testing, and verification:
- `fix/`: Scripts to fix S3 storage issues
- `tests/`: Scripts to test S3 functionality
- `utils/`: Utility scripts for S3
- `verification/`: Scripts to verify S3 configuration

### Fix Scripts (`scripts/fixes/`)
Scripts to fix various issues in the application:
- `http/`: HTTP fix scripts
- `s3/`: S3 fix scripts

### Media Scripts (`scripts/media/`)
Scripts for media file handling:
- `serve_media.py`: Serve media files over HTTP
- `verify_image_urls.py`: Verify image URLs are accessible
- `utils/`: Media utility scripts

### Workflow Scripts (`scripts/workflow/`)
Scripts for managing Replit workflow configuration:
- `update_workflow.py`: Update Replit workflow configuration
- `organize_http_files.sh`: Organize HTTP files in the project
- `workflow_server.py`: Helper for workflow server configuration

## Main Scripts

The following scripts live in the `scripts/` directory:

- `run_app`: Main entry point for the application
- `run_art_critique.sh`: Full-featured runner with options
- `run.sh`: Legacy wrapper that starts the HTTP-mode server
- `run_http.sh`: Start the server in HTTP mode after applying fixes
- `run_http_only.sh`: Minimal HTTP server launcher

## Running the Application

```bash
# Start the application with default options (HTTP mode)
./scripts/run_app

# Specify options (HTTP mode with S3 storage)
./scripts/run_app --http --with-s3

# Run tests
./scripts/run_app --test
./scripts/run_app --test=http  # Run only HTTP tests
```

## Common Tasks

### Starting the Server
```bash
./scripts/run_app
```

### Running Tests
```bash
./scripts/run_app --test
```

### Fixing S3 Issues
```bash
python scripts/fixes/s3/fix_s3_permissions.py
```

### Fixing HTTP Issues
```bash
python scripts/fixes/http/fix_ssl_issue.py
python scripts/fixes/http/fix_http_server.py
python scripts/fixes/http/fix_server_ssl.py
```
