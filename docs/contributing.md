# Contributing to signalrgb-python

Contributions are welcome. This guide covers how to get involved.

## 🧐 Before you start

### Project structure

- `signalrgb/` — library source (client, async_client, cli, model, exceptions, constants)
- `tests/` — pytest suite (unit tests for client, async client, CLI, and models)
- `docs/` — MkDocs documentation (published to GitHub Pages on tag push)
- `examples/` — example scripts
- `.github/workflows/` — CI, publish, docs, and release workflows

See the [Development Guide](development.md) for environment setup and the task runner.

## 🤝 How to contribute

### 🐛 Reporting bugs

When filing a bug report:

- Use a clear, descriptive title
- Describe the exact steps to reproduce
- Include the SignalRGB version, signalrgb-python version, and Python version
- Paste any relevant tracebacks or error messages
- Describe what you expected vs. what happened

### 💡 Suggesting enhancements

- Use a clear, descriptive title
- Explain the motivation — what problem does this solve?
- Describe the proposed API or behavior
- Mention any alternatives you considered

### 🎯 Your first code contribution

Good starting points:

- [Good first issues](https://github.com/hyperb1iss/signalrgb-python/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) — small, well-scoped issues
- [Help wanted](https://github.com/hyperb1iss/signalrgb-python/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22) — issues that need attention

### 📥 Pull requests

- Branch from `main` and open the PR against `main`
- Run `just verify` before pushing — CI runs the same checks
- Include tests for new functionality in `tests/`
- Write Google-style docstrings for public functions and methods
- Keep commits focused and descriptive

## 📝 Style guide

### Git commit messages

- Use imperative mood ("Add feature" not "Added feature")
- Limit the first line to ~72 characters
- Use [gitmoji](https://gitmoji.dev/) prefixes if you like — common examples:
  - `:art:` — code structure / formatting
  - `:bug:` — bug fix
  - `:sparkles:` (reserved — we don't use ✨ per style guide)
  - `:fire:` — removing code or files
  - `:memo:` — docs
  - `:white_check_mark:` — tests
  - `:lock:` — security
  - `:arrow_up:` — upgrade deps
  - `:wrench:` — config change
  - `:rocket:` (reserved — we don't use 🚀 per style guide)

### Python style

- **ruff** handles formatting and linting — `just fmt` + `just lint-fix`
- **ty** handles type checking — `just typecheck`
- Follow [PEP 8](https://peps.python.org/pep-0008/) (ruff enforces this)
- Use Google-style docstrings for public API
- Add type hints to all public functions and methods
- Target Python 3.11+

### Documentation style

- Markdown for all docs
- One emoji per heading max (the SilkCircuit style guide bans 🚀 ✨ 💯 🙏 🎉 👀 👍)
- Use emoji in headings for visual scanning, not in body text
- Keep docs in sync with code — update `docs/` alongside feature PRs

## 📋 Issue labels

| Label | Meaning |
| --- | --- |
| `bug` | Something is broken |
| `enhancement` | Feature request or improvement |
| `question` | Needs discussion |
| `duplicate` | Already tracked elsewhere |
| `good first issue` | Good for newcomers |
| `help wanted` | Community help appreciated |
| `documentation` | Docs-only change |
| `performance` | Performance-related |
| `security` | Security-related |

## Thanks 💜

Thanks for contributing. Every bug report, suggestion, and PR helps.
