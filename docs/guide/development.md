# Development

## Prerequisites

- **Python 3.13+**
- [uv](https://github.com/astral-sh/uv) — packaging and dependency management
- [just](https://github.com/casey/just) — task runner (optional but recommended)

## Setup

```bash
git clone https://github.com/hyperb1iss/signalrgb-python.git
cd signalrgb-python
just install
```

## Common tasks

| Task                        | Command                          |
| --------------------------- | -------------------------------- |
| Full check suite            | `just verify`                    |
| Fast loop (auto-fix)        | `just check`                     |
| Tests with coverage         | `just test`                      |
| Tests without coverage      | `just test-fast`                 |
| Run a single test           | `just test-one test_get_effects` |
| Lint                        | `just lint`                      |
| Auto-fix lint               | `just lint-fix`                  |
| Format Python               | `just fmt`                       |
| Format prose (md/yaml/json) | `just prose`                     |
| Type-check                  | `just typecheck`                 |
| Docs dev server             | `just docs-serve`                |
| Run the CLI                 | `just run effect list`           |
| See all tasks               | `just --list`                    |

## Toolchain

- **ruff** — linting and formatting
- **ty** — type checking (Astral's Rust type checker)
- **pytest** — test framework with asyncio auto mode and branch coverage
- **prettier** — Markdown, YAML, and JSON formatting

## Release flow

Releases are driven by GitHub Actions — no local script needed.

```bash
just release              # patch bump
just release minor        # minor bump
just release-version 2.0.0
```

The `release.yml` workflow bumps the version, commits, tags, and pushes. The tag push triggers
`publish.yml` (PyPI via OIDC) and `docs.yml` (VitePress → GitHub Pages).
