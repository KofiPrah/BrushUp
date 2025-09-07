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

## Running the Application

The project now ships with a single CLI that replaces the numerous
`start_*` and `run_*` scripts previously used in the repository.

```bash
python scripts/cli.py serve
```

Common options:

```bash
python scripts/cli.py serve --protocol https --ssl    # enable HTTPS
python scripts/cli.py serve --server gunicorn         # use gunicorn
python scripts/cli.py serve --workflow                # run setup fixes
```

## Running Tests

Run the test suite with:

```bash
pytest
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