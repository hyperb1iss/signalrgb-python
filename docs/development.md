# Development Guide

This guide will help you set up your development environment for contributing to signalrgb-python.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- Python 3.12 or higher
- [Poetry](https://python-poetry.org/docs/#installation) for dependency management
- Git for version control

## Setting Up the Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/hyperb1iss/signalrgb-python.git
   cd signalrgb-python
   ```

2. Install the project dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Activate the virtual environment:
   ```bash
   poetry shell
   ```

## Running Tests

We use pytest for our test suite. To run the tests:

```bash
poetry run pytest
```

To run tests with coverage report:

```bash
poetry run pytest --cov=signalrgb --cov-report=term-missing
```

## Linting

We use Ruff for linting and formatting. To run the linter:

```bash
poetry run ruff check .
```

To automatically fix linting issues:

```bash
poetry run ruff check --fix .
```

## Type Checking

We use mypy for static type checking. To run the type checker:

```bash
poetry run mypy signalrgb
```

## Pre-commit Hooks

We use pre-commit hooks to ensure code quality before committing. To set up pre-commit hooks:

1. Install pre-commit:
   ```bash
   poetry run pre-commit install
   ```

2. Run pre-commit on all files:
   ```bash
   poetry run pre-commit run --all-files
   ```

The pre-commit hooks will now run automatically on `git commit`.

## Building Documentation

To build the documentation locally:

1. Install the documentation dependencies:
   ```bash
   poetry add mkdocs mkdocs-material mkdocstrings[python]
   ```

2. Build and serve the documentation:
   ```bash
   poetry run mkdocs serve
   ```

3. Open your browser and navigate to `http://127.0.0.1:8000/` to view the documentation.

## Creating a New Release

1. Update the version number in `pyproject.toml`:
   ```bash
   poetry version patch  # or minor, or major
   ```

2. Update the `CHANGELOG.md` file with the changes for the new version.

3. Commit the changes:
   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "Bump version to x.y.z"
   ```

4. Create a new tag:
   ```bash
   git tag -a vx.y.z -m "Release version x.y.z"
   ```

5. Push the changes and the new tag:
   ```bash
   git push origin main --tags
   ```

The CI/CD pipeline will handle the rest, including building and publishing the package to PyPI and deploying the updated documentation.

## Troubleshooting

If you encounter any issues during development, please check the following:

1. Ensure you're using the correct version of Python (3.12+).
2. Make sure all dependencies are up to date (`poetry update`).
3. Check that your virtual environment is activated (`poetry shell`).
4. Clear any cached files: `find . -name '*.pyc' -delete` and `find . -name '__pycache__' -type d -delete`

If you're still having problems, please open an issue on the GitHub repository with a detailed description of the problem and steps to reproduce it.

## Getting Help

If you need help with development, you can:

1. Open an issue on the GitHub repository.
2. Reach out to the maintainers directly (contact information can be found in the `README.md` file).

