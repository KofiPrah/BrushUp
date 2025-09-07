# Art Critique 

A Django-powered web application that provides a comprehensive platform for art professionals to share, critique, and engage with creative works through innovative digital interactions.

## Key Components
- Django web framework with RESTful API infrastructure
- OAuth-enabled Google authentication
- React.js frontend with responsive design
- HTTP mode configuration with flexible deployment options
- S3 storage integration for media management
- Secure user profile and artwork management system

## Project Structure

The project is organized into the following directories:

- `artcritique/`: Main Django application
- `critique/`: Artwork critique functionality
- `docs/`: Documentation
  - `api/`: API documentation
  - `auth/`: Authentication documentation
  - `replit/`: Replit-specific documentation
  - `s3/`: S3 storage documentation
  - `server/`: Server documentation
- `scripts/`: Scripts for running and managing the application
  - `fixes/`: Fix scripts
    - `http/`: HTTP fix scripts
    - `s3/`: S3 fix scripts
  - `http/`: HTTP server scripts
    - `config/`: HTTP configuration files
    - `modules/`: HTTP Python modules
    - `runners/`: HTTP server runners
  - `media/`: Media handling scripts
    - `utils/`: Media utilities
  - `s3/`: S3 storage scripts
    - `fix/`: S3 fix scripts
    - `tests/`: S3 test scripts
    - `utils/`: S3 utilities
    - `verification/`: S3 verification scripts
  - `workflow/`: Workflow management scripts
- `tests/`: Test scripts
  - `api/`: API tests
  - `auth/`: Authentication tests
  - `deployment/`: Deployment tests
  - `frontend/`: Frontend tests
  - `http/`: HTTP server tests
  - `media/`: Media handling tests
    - `test-images/`: Test image files
  - `s3/`: S3 storage tests

## Dependency Management

Dependencies are defined in `pyproject.toml` and locked with `uv.lock`.
Use `uv` to sync and lock dependencies:

```bash
uv sync      # install dependencies from the lock file
uv lock      # regenerate uv.lock after modifying dependencies
```

The legacy `project_requirements.txt` file has been removed.

## Running the Application

The simplest way to run the application is:

```bash
./run_app
```

You can also specify options:

```bash
./run_app --http     # Start with HTTP mode (default, recommended for Replit)
./run_app --https    # Start with HTTPS mode
./run_app --with-s3  # Enable S3 storage (requires AWS credentials)
```

## Running Tests

You can run all tests with:

```bash
./run_app --test
```

Or run specific test categories:

```bash
./run_app --test=http    # Run HTTP tests
./run_app --test=api     # Run API tests
./run_app --test=auth    # Run authentication tests
./run_app --test=s3      # Run S3 tests
./run_app --test=media   # Run media tests
```

## Documentation

For more detailed documentation, see the `docs/` directory, which includes:

- API documentation
- Authentication setup
- S3 storage configuration
- Deployment guides
- Replit configuration

## Replit Configuration

To configure the application for Replit, see [WORKFLOW_CONFIG.md](WORKFLOW_CONFIG.md).