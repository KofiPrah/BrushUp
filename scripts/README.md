# Art Critique Scripts

This directory contains scripts for running, managing, and fixing the Art Critique application.

## Categories

### HTTP Scripts (`scripts/http/`)
Scripts for HTTP server configuration and management:
- `run_server.sh`: Main script to run the HTTP server
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

The following scripts are available in the root directory for easy access:

- `run_app`: Main entry point for the application
- `run_art_critique.sh`: Full-featured runner with options
- `run_server.sh`: Simplified server runner

## Running the Application

```bash
# Start the application with default options (HTTP mode)
./run_app

# Specify options (HTTP mode with S3 storage)
./run_app --http --with-s3

# Run tests
./run_app --test
./run_app --test=http  # Run only HTTP tests
```

## Common Tasks

### Starting the Server
```bash
./run_app
```

### Running Tests
```bash
./run_app --test
```

### Fixing S3 Issues
```bash
python scripts/fixes/s3/fix_s3_permissions.py
```

### Fixing HTTP Issues
```bash
python scripts/fixes/http/fix_ssl_issue.py
```