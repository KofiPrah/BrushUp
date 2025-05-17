# Art Critique Project Overview

Art Critique is a Django-powered web application that provides a comprehensive platform for art professionals to share, critique, and engage with creative works through innovative digital interactions.

## Key Components

- **Django Web Framework**: Backend infrastructure with RESTful API support
- **Authentication**: OAuth-enabled Google authentication
- **Frontend**: React.js with responsive design
- **Storage**: AWS S3 integration for media files
- **Database**: PostgreSQL for data storage

## Project Structure

The project is organized into the following directories:

- `artcritique/`: Main Django application 
- `critique/`: Artwork critique functionality
- `docs/`: Project documentation
  - `api/`: API documentation
  - `auth/`: Authentication documentation
  - `aws/`: AWS integration documentation
  - `deployment/`: Deployment guides
  - `replit/`: Replit-specific documentation
  - `s3/`: S3 storage documentation
- `scripts/`: Utility scripts
  - `http/`: HTTP server scripts
  - `s3/`: S3 storage scripts
- `tests/`: Test scripts
  - `api/`: API tests
  - `auth/`: Authentication tests
  - `http/`: HTTP server tests
  - `media/`: Media handling tests
  - `s3/`: S3 storage tests
- `static/`: Static files
- `templates/`: HTML templates
- `media/`: Local media storage (when not using S3)

## HTTP Mode Configuration

To run the application with Replit's load balancer, you need to use HTTP mode:

1. Use the `start_http.sh` script to start the server without SSL:
   ```
   ./start_http.sh
   ```

2. To permanently update the Replit workflow:
   - Open the `.replit` file
   - Change the command to: `./start_http.sh`
   - Set `SSL_ENABLED` to `false`

See `docs/replit/SSL_HTTP_FIX.md` for detailed instructions.

## S3 Storage Configuration

The application can store media files either locally or in AWS S3:

- Set `USE_S3=True` to use AWS S3 storage
- Configure AWS credentials in environment variables
- See `docs/s3/S3_CONFIGURATION.md` for detailed setup

## Running Tests

Use the test runner script to run tests:

```
./scripts/run_all_tests.sh
```

You can run specific test categories:
```
./scripts/run_all_tests.sh --http-only  # Run only HTTP tests
./scripts/run_all_tests.sh --s3-only    # Run only S3 tests
```

## Documentation

See the `docs/` directory for detailed documentation on all aspects of the application.