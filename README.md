# 🌈 signalrgb-python

<div align="center">

[![CI](https://github.com/hyperb1iss/signalrgb-python/actions/workflows/ci.yml/badge.svg)](https://github.com/hyperb1iss/signalrgb-python/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyPI version](https://img.shields.io/pypi/v/signalrgb)](https://pypi.org/project/signalrgb)
[![Python](https://img.shields.io/pypi/pyversions/signalrgb)](https://pypi.org/project/signalrgb)

_A Python client library and CLI for controlling [SignalRGB Pro](https://signalrgb.com)_

[Features](#features) • [Installation](#installation) • [Usage](#usage) •
[API Reference](#api-reference) • [Development](#development) • [Contributing](#contributing) •
[License](#license)

</div>

## 🌟 Features

<a name="features"></a>

- List available lighting effects, presets, and layouts
- Apply effects, presets, and layouts to your devices
- Control canvas brightness and enabled state
- Synchronous client for scripts and tools
- Asynchronous client (httpx) for asyncio apps and Home Assistant integrations
- Rich-powered CLI with intuitive subcommands (`effect`, `preset`, `layout`, `canvas`)
- Effect caching and robust exception types for connection, API, and not-found errors

## 💎 Installation

<a name="installation"></a>

```bash
# with uv (recommended)
uv add signalrgb

# or with pip
pip install signalrgb
```

### Prerequisites

- Python **3.13+**
- [SignalRGB Pro](https://www.signalrgb.com/pro/) — required for API access

This library uses the [SignalRGB REST API](https://docs.signalrgb.com/signalrgb-api), which is only
available in SignalRGB Pro.

## 🎯 Usage

<a name="usage"></a>

### Command-line interface

The CLI is a Rich + Typer app with category subcommands for effects, presets, layouts, and canvas
control.

```bash
# Effects
signalrgb effect list
signalrgb effect "Psychedelic Dream"
signalrgb effect apply "Rave Visualizer"
signalrgb effect random
signalrgb effect search "ocean"

# Presets
signalrgb preset list
signalrgb preset apply "My Fancy Preset"

# Layouts
signalrgb layout list
signalrgb layout set "My Gaming Layout"

# Canvas
signalrgb canvas                     # show state + brightness
signalrgb canvas brightness 75       # set brightness
signalrgb canvas brightness          # read brightness
signalrgb canvas enable
signalrgb canvas disable
signalrgb canvas toggle
```

Point at a remote SignalRGB instance:

```bash
signalrgb --host hyperia.home --port 16038 effect list
```

Full help:

```bash
signalrgb --help
```

### Synchronous client

```python
from signalrgb import SignalRGBClient

client = SignalRGBClient(host="hyperia.home", port=16038)

# List effects
for effect in client.get_effects():
    print(effect.attributes.name)

# Apply an effect and a preset
client.apply_effect_by_name("Rain")
current = client.get_current_effect()
client.apply_effect_preset(current.id, "Cool Preset")

# Canvas control
client.brightness = 50
client.enabled = True
```

### Asynchronous client

For async apps and Home Assistant integrations, use `AsyncSignalRGBClient` as an async context
manager:

```python
import asyncio
from signalrgb import AsyncSignalRGBClient

async def main() -> None:
    async with AsyncSignalRGBClient(host="hyperia.home", port=16038) as client:
        for effect in await client.get_effects():
            print(effect.attributes.name)

        await client.apply_effect_by_name("Rain")
        await client.set_brightness(75)
        await client.set_enabled(True)

        current = await client.get_current_effect()
        print(f"Current effect: {current.attributes.name}")

asyncio.run(main())
```

See [docs/async_usage.md](docs/async_usage.md) for the full async guide.

### Error handling

```python
from signalrgb import SignalRGBClient, ConnectionError, APIError, NotFoundError

client = SignalRGBClient()

try:
    client.apply_effect_by_name("Non-existent Effect")
except ConnectionError as e:
    print(f"Connection failed: {e}")
except NotFoundError as e:
    print(f"Effect not found: {e}")
except APIError as e:
    print(f"API error: {e}")
```

The same pattern works with the async client.

## 🔮 API Reference

<a name="api-reference"></a>

Full API docs are published at **<https://hyperb1iss.github.io/signalrgb-python/>**.

## 🧪 Development

<a name="development"></a>

The project uses the Astral stack: **uv** for packaging, **ruff** for lint + format, **ty** for type
checking, and **pytest** for tests. All common tasks are wired up in the `justfile`.

```bash
# Clone and set up
git clone https://github.com/hyperb1iss/signalrgb-python.git
cd signalrgb-python

# Install everything (runtime + dev + docs)
just install

# Run the full check suite (lint, format, typecheck, tests)
just verify

# Or the fast loop (auto-fix then test)
just check

# Other common tasks
just test              # pytest with coverage
just lint-fix          # ruff check --fix
just fmt               # ruff format
just typecheck         # ty check
just docs-serve        # mkdocs on :8000
just run effect list   # run the CLI
just --list            # see everything
```

See the [Development Guide](https://hyperb1iss.github.io/signalrgb-python/development/) for the full
workflow.

## 🦋 Contributing

<a name="contributing"></a>

Contributions are welcome. Fork, branch, and open a PR:

1. Fork the repository
2. Create a branch: `git checkout -b my-feature`
3. `just verify` should pass before you push
4. Open a pull request

Please include tests for new functionality and follow the existing code style (ruff + ty will tell
you if anything's off).

## 📄 License

<a name="license"></a>

Apache License 2.0 — see [LICENSE](LICENSE).

---

<div align="center">

[Documentation](https://hyperb1iss.github.io/signalrgb-python/) •
[Report a bug](https://github.com/hyperb1iss/signalrgb-python/issues) •
[Request a feature](https://github.com/hyperb1iss/signalrgb-python/issues)

</div>

## 💜 Acknowledgements

This project is not officially associated with SignalRGB. It is an independent community client —
please do not report client issues to the SignalRGB team.

---

<div align="center">

Created by [Stefanie Jane](https://github.com/hyperb1iss)

If you find this project useful, consider
[buying me a Monster Ultra Violet](https://ko-fi.com/hyperb1iss).

</div>
