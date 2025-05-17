# Art Critique Tests

This directory contains tests for various components of the Art Critique application.

## Test Categories:
- [Authentication Tests](auth/README.md) - Tests for user authentication
- [API Tests](api/README.md) - Tests for API endpoints
- [S3 Storage Tests](s3/README.md) - Tests for AWS S3 integration
- [Media Tests](media/README.md) - Tests for image uploads and media handling
- [HTTP Tests](http/README.md) - Tests for HTTP server configuration
- [Frontend Tests](frontend/README.md) - Tests for frontend components
- [Deployment Tests](deployment/README.md) - Tests for deployment configurations

## Running Tests
Use the test runner script to run all tests:

```bash
./scripts/run_all_tests.sh
```

Or run specific test categories:

```bash
./scripts/run_all_tests.sh --http-only  # Run only HTTP tests
./scripts/run_all_tests.sh --s3-only    # Run only S3 tests
```

## Test Images
Test images are stored in `media/test-images/` directory.
