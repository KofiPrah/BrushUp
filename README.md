# Brush Up – Art Critique Platform

Brush Up is a Django‑powered web application where art professionals can share works, exchange critiques, and build community.

## Features

- Google OAuth authentication
- Artwork uploads backed by Amazon S3
- Reaction‑based critiques (Helpful, Inspiring, Detailed)
- Karma system rewarding community contributions
- Responsive gallery with search and filter support

## Project structure

The repository is organized into key directories:

- `artcritique/` – core Django project
- `critique/` – critique functionality
- `frontend/` – React frontend assets
- `docs/` – in‑depth documentation
- `scripts/` – utility and helper scripts
- `tests/` – automated test suite
- `static/` & `templates/` – front‑end files

## Running the application

Use the unified CLI to start the server in HTTP mode (port 5000 by default):

```bash
python start_brushup.py
```

The script applies required serializer fixes and launches the app without SSL, which suits environments like Replit that handle HTTPS termination.

## Running tests

Run the full test suite via the provided helper script:

```bash
scripts/run_all_tests.sh
```

## Documentation

Extensive guides are available under the `docs/` directory for deeper topics:

- [API guides](docs/api/)
- [Authentication](docs/auth/)
- [S3 configuration](docs/s3/)
- [Deployment](docs/deployment/)
- [Replit setup](docs/replit/)

