# HTTP Server Scripts

This directory contains scripts for running the Art Critique application in HTTP mode.

## Primary Scripts

- `run_http_server.sh`: Main script to run the server in HTTP mode
- `http_main.py`: HTTP-specific entry point for the Django application

## Usage

From the project root directory, run:

```bash
./scripts/http/run_http_server.sh
```

Or use the wrapper script:

```bash
./run_server.sh --http
```

## Script Descriptions

- `run_http_server.sh`: Starts Gunicorn in HTTP mode
- `http_main.py`: Modified main module that forces HTTP mode
- `http_server_settings.py`: Configuration module for HTTP mode
