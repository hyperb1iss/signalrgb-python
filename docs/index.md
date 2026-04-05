# signalrgb-python

A Python client library and CLI for controlling [SignalRGB Pro](https://signalrgb.com) through synchronous and asynchronous APIs.

## 🌟 Features

- List available lighting effects, presets, and layouts
- Apply effects, presets, and layouts
- Control canvas brightness and enabled state
- Synchronous client for scripts and tools
- Asynchronous client (httpx) for asyncio applications and Home Assistant integrations
- Rich-powered CLI with `effect`, `preset`, `layout`, and `canvas` subcommands
- Effect caching and typed exceptions for connection, API, and not-found errors

## 🎯 Quick Start

### Installation

```bash
uv add signalrgb    # or: pip install signalrgb
```

### Command-line interface

```bash
signalrgb effect list
signalrgb effect apply "Rainbow Wave"
signalrgb canvas brightness 75
signalrgb canvas enable
```

### Synchronous Python API

```python
from signalrgb import SignalRGBClient

client = SignalRGBClient()

client.apply_effect_by_name("Rainbow Wave")
client.brightness = 75
client.enabled = True

effect = client.get_current_effect()
print(f"Current effect: {effect.attributes.name}")
```

### Asynchronous Python API

```python
import asyncio
from signalrgb import AsyncSignalRGBClient

async def main() -> None:
    async with AsyncSignalRGBClient() as client:
        await client.apply_effect_by_name("Rainbow Wave")
        await client.set_brightness(75)

        effect = await client.get_current_effect()
        print(f"Current effect: {effect.attributes.name}")

asyncio.run(main())
```

## 📚 Documentation

- **[Installation](installation.md)** — detailed installation instructions
- **Usage guides**
  - [Command-Line Interface](usage/cli.md) — using the SignalRGB CLI
  - [Synchronous Library](usage/library.md) — using the Python library in sync code
  - [Asynchronous Library](async_usage.md) — using the async client with asyncio
- **API reference**
  - [Client API](api/client.md) — `SignalRGBClient` and `AsyncSignalRGBClient`
  - [Models](api/models.md) — data model reference
- **Development**
  - [Contributing](contributing.md) — contribution guidelines
  - [Development Guide](development.md) — dev environment setup
