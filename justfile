# signalrgb-python — Developer Commands
# Usage: just <recipe>    List: just --list

set dotenv-load := false
set positional-arguments := true

# Show available recipes (default when running `just` with no arguments)
[private]
default:
    @just --list

# ─── Aliases ──────────────────────────────────────────────

alias i := install
alias t := test
alias l := lint
alias f := fmt
alias c := check
alias v := verify

# ─── Core ─────────────────────────────────────────────────

# Install all dependencies (dev + docs groups)
install:
    uv sync --all-groups

# Install only runtime + dev (skip docs/release for faster CI loops)
install-dev:
    uv sync

# Run every check — lint, format, typecheck, tests
verify: lint fmt-check typecheck test
    @echo '\033[38;2;80;250;123m✅ All checks passed\033[0m'

# Fast local loop — lint + typecheck + tests, auto-fixing what it can
check: lint-fix fmt typecheck test

# ─── Testing ──────────────────────────────────────────────

# Run the full test suite with coverage
test *args='':
    uv run pytest {{ args }}

# Run tests without coverage (fastest)
test-fast *args='':
    uv run pytest --no-cov {{ args }}

# Run a single test by name or path
test-one name *args='':
    uv run pytest -k {{ name }} {{ args }}

# Generate HTML coverage report and open it
test-cov:
    uv run pytest --cov-report=html
    @echo '\033[38;2;128;255;234m→ open htmlcov/index.html\033[0m'

# Watch mode — rerun tests on file changes (requires pytest-watch)
test-watch *args='':
    uv run --with pytest-watch ptw -- {{ args }}

# ─── Linting & Formatting ────────────────────────────────

# Lint with ruff
lint *args='':
    uv run ruff check . {{ args }}

# Auto-fix lint issues
lint-fix *args='':
    uv run ruff check --fix . {{ args }}

# Auto-fix including unsafe fixes (review the diff!)
lint-fix-unsafe:
    uv run ruff check --fix --unsafe-fixes .

# Format all code
fmt:
    uv run ruff format .

# Check formatting without modifying
fmt-check:
    uv run ruff format --check .

# Explain a ruff rule (e.g. `just rule PLR0913`)
rule code:
    uv run ruff rule {{ code }}

# ─── Type Checking ───────────────────────────────────────

# Type-check with ty
typecheck *args='':
    uv run ty check {{ args }}

# Alias
ty *args='': (typecheck args)

# Explain a ty rule (e.g. `just ty-rule unresolved-import`)
ty-rule rule:
    uv run ty explain {{ rule }}

# ─── Running ──────────────────────────────────────────────

# Run the signalrgb CLI (e.g. `just run effect list`)
run *args='':
    uv run signalrgb "$@"

# Show CLI help
help:
    uv run signalrgb --help

# Run the async example script
example-async:
    uv run python examples/async_example.py

# ─── Documentation ───────────────────────────────────────

# Serve docs locally with hot reload (http://127.0.0.1:8000)
docs-serve:
    uv run --group docs mkdocs serve

# Build docs into ./site
docs-build:
    uv run --group docs mkdocs build

# Deploy docs to gh-pages branch (CI does this automatically)
docs-deploy:
    uv run --group docs mkdocs gh-deploy --force

# ─── Build & Release ─────────────────────────────────────

# Build sdist + wheel into ./dist
build:
    uv build

# Preview what will be included in the build
build-list:
    uv build --list

# Trigger the GitHub Actions release workflow (bump + tag + publish)
# Examples:
#   just release                  # patch bump
#   just release minor            # minor bump
#   just release major            # major bump
#   just release patch true       # dry run
release bump='patch' dry_run='false':
    gh workflow run release.yml \
        -f bump={{ bump }} \
        -f dry_run={{ dry_run }}
    @echo '\033[38;2;128;255;234m→ Watch the run: gh run watch\033[0m'

# Trigger a release with an explicit version (e.g. `just release-version 1.2.0`)
release-version version dry_run='false':
    gh workflow run release.yml \
        -f version={{ version }} \
        -f dry_run={{ dry_run }}
    @echo '\033[38;2;128;255;234m→ Watch the run: gh run watch\033[0m'

# Dry-run a local version bump (preview only — doesn't write)
version-bump kind='patch':
    uv version --bump {{ kind }} --dry-run

# ─── Dependencies ────────────────────────────────────────

# Lock dependencies from pyproject.toml
lock:
    uv lock

# Upgrade all deps to latest compatible versions
upgrade:
    uv lock --upgrade
    uv sync --all-groups

# Upgrade a single package (e.g. `just upgrade-package httpx`)
upgrade-package pkg:
    uv lock --upgrade-package {{ pkg }}
    uv sync --all-groups

# Show dependency tree
tree *args='':
    uv tree {{ args }}

# Audit dependencies for vulnerabilities (preview feature)
audit:
    uv audit --preview

# ─── Pre-commit ──────────────────────────────────────────

# Install pre-commit hooks
hooks-install:
    uv run pre-commit install

# Run pre-commit on all files
hooks-run:
    uv run pre-commit run --all-files

# Update pre-commit hook versions
hooks-update:
    uv run pre-commit autoupdate

# ─── Housekeeping ────────────────────────────────────────

# Remove build artifacts, caches, and coverage data
clean:
    rm -rf build dist site htmlcov .coverage .pytest_cache .ruff_cache .mypy_cache
    find . -type d -name __pycache__ -prune -exec rm -rf {} +
    find . -type d -name '*.egg-info' -prune -exec rm -rf {} +
    @echo '\033[38;2;80;250;123m✅ Cleaned\033[0m'

# Nuke the virtualenv and reinstall from scratch
reset:
    rm -rf .venv
    uv sync --all-groups
    @echo '\033[38;2;80;250;123m✅ Fresh venv ready\033[0m'

# Show signalrgb package info
info:
    @uv run python -c "import signalrgb; print(f'signalrgb {signalrgb.__version__}')"
    @uv tree --depth 1
