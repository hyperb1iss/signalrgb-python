# Installation

## 🧰 Prerequisites

- **Python 3.13 or higher**
- [SignalRGB Pro](https://www.signalrgb.com/pro/) — required for API access

This library uses the [SignalRGB REST API](https://docs.signalrgb.com/signalrgb-api), which is only available in SignalRGB Pro.

### Async client requirements

The `AsyncSignalRGBClient` has no extra dependencies beyond the base install — httpx is already required. For integration with Home Assistant or other asyncio frameworks, see the [Async Usage](async_usage.md) guide.

## 💎 Installing with uv

[uv](https://github.com/astral-sh/uv) is the recommended way to manage Python projects and dependencies.

```bash
# Add signalrgb to an existing uv project
uv add signalrgb

# Or install it as a global tool (CLI only)
uv tool install signalrgb
```

## 📦 Installing with pip

```bash
pip install signalrgb
```

## 🧪 Development installation

If you're working on signalrgb-python itself:

```bash
git clone https://github.com/hyperb1iss/signalrgb-python.git
cd signalrgb-python

# Install runtime + dev + docs dependency groups
uv sync --all-groups

# Or use the justfile shortcut
just install
```

## ✅ Verifying the installation

```bash
signalrgb --help
```

And from a Python shell:

```python
import signalrgb
print(signalrgb.__version__)
```

## 📚 Next steps

- [CLI Usage](usage/cli.md) — command-line interface guide
- [Python Library Usage](usage/library.md) — synchronous API
- [Async Library Usage](async_usage.md) — asynchronous API
