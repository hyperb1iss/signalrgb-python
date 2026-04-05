# Development Guide

This guide covers setting up your development environment for signalrgb-python.

## 🧰 Prerequisites

- **Python 3.13 or higher**
- [uv](https://github.com/astral-sh/uv) for packaging and dependency management
- [just](https://github.com/casey/just) for task running (optional but recommended)
- Git

## 🎯 Setup

```bash
git clone https://github.com/hyperb1iss/signalrgb-python.git
cd signalrgb-python

# Install runtime + dev + docs groups
just install            # or: uv sync --all-groups
```

All development tasks are wired up in the `justfile`. Run `just --list` to see everything.

## 🧪 Running tests

```bash
just test                      # pytest with coverage (default)
just test-fast                 # skip coverage for speed
just test-one test_get_effects # run a single test by name
just test-cov                  # HTML coverage report in htmlcov/
```

Under the hood this runs `uv run pytest` with the config in `pyproject.toml` (asyncio auto mode, strict markers, branch coverage).

## 🔍 Linting and formatting

We use [ruff](https://github.com/astral-sh/ruff) for both linting and formatting.

```bash
just lint            # ruff check
just lint-fix        # ruff check --fix
just fmt             # ruff format
just fmt-check       # ruff format --check
just rule PLR0913    # explain a specific ruff rule
```

## 🧪 Type checking

We use [ty](https://github.com/astral-sh/ty), Astral's Rust-based type checker.

```bash
just typecheck              # ty check
just ty-rule unresolved-import   # explain a specific rule
```

ty is currently in beta (0.0.x) — it's faster than mypy and integrates with the same `[tool.ty]` section of `pyproject.toml`.

## 🎯 The verify loop

Before pushing, run the full check suite:

```bash
just verify            # lint + fmt-check + typecheck + test
```

`just verify` is exactly what CI runs, so if it passes locally, CI should pass too.

For a fast local iteration loop that auto-fixes what it can:

```bash
just check             # lint-fix + fmt + typecheck + test
```

## 🔄 Pre-commit hooks

```bash
just hooks-install     # install hooks
just hooks-run         # run on all files
just hooks-update      # bump hook versions
```

The hooks run ruff (check + format) and ty on every commit.

## 📚 Building the docs

```bash
just docs-serve        # live-reloading mkdocs on http://127.0.0.1:8000
just docs-build        # build into ./site
```

## 💎 Creating a new release

Releases run through GitHub Actions — no local script needed.

Trigger the release workflow via the `just` helper or the GitHub UI:

```bash
# Auto-bump patch version
just release

# Bump minor or major
just release minor
just release major

# Explicit version
just release-version 1.2.0

# Dry run (no commit/tag/push)
just release patch true
```

The workflow (`release.yml`) will:

1. Compute the new version (from `bump` or explicit `version` input)
2. Run `uv version` + `uv lock` + patch `__version__` in `signalrgb/__init__.py`
3. Run `uv build` as a smoke test
4. Commit, tag `v<version>`, and push

Pushing the tag automatically triggers `publish.yml` (PyPI via OIDC trusted publishing) and `docs.yml` (MkDocs → GitHub Pages).

## 🐛 Troubleshooting

- **Dependency issues**: `uv lock` out of sync with `pyproject.toml`? Run `uv sync --all-groups` or `just install`.
- **Stale caches**: `just clean` removes build artifacts, coverage, `__pycache__`, and ruff/ty caches.
- **Broken venv**: `just reset` nukes `.venv` and reinstalls from scratch.
- **Ruff/ty version mismatch**: `uv lock --upgrade` pulls the latest, or `just upgrade-package ruff`.

## 💬 Getting help

- Open an issue on the [GitHub repository](https://github.com/hyperb1iss/signalrgb-python/issues)
- Check existing docs under `docs/` or the published site
