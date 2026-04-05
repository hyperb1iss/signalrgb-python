# Contributing

Contributions welcome. Fork, branch, and open a PR.

## Workflow

1. Fork the repo and clone your fork
2. `just install` to set up the dev environment
3. Create a branch: `git checkout -b my-feature`
4. Make changes — `just check` auto-fixes and runs the full suite
5. `just verify` must pass before you push
6. Open a pull request against `main`

## Style

- **ruff** handles Python formatting and linting — `just fmt` + `just lint-fix`
- **ty** handles type checking — `just typecheck`
- **prettier** handles Markdown/YAML/JSON — `just prose`
- Google-style docstrings for public API
- Type hints on all public functions and methods
- Target Python 3.13+

## Commit messages

Use imperative mood ("Add feature" not "Added feature"), ~72 char first line. Gitmoji prefixes
optional — just don't use the banned ones (🚀 ✨ 💯 🙏 🎉 👀 👍).

## Tests

Include tests for new functionality in `tests/`. The test suite uses pytest with asyncio auto mode.

```bash
just test-fast              # quick validation
just test                   # with coverage
just test-one my_test_name  # single test
```

## Reporting bugs

- Clear, descriptive title
- Steps to reproduce
- Python version + signalrgb-python version + SignalRGB version
- Error output / traceback

## Thanks 💜
