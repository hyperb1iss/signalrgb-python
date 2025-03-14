# signalrgb-python

Welcome to the documentation for signalrgb-python! This library provides a powerful and easy-to-use interface for controlling [SignalRGB Pro](https://signalrgb.com) through both a command-line interface (CLI) and Python libraries (both synchronous and asynchronous).

## ✨ Features

- 📋 List available lighting effects and presets
- 🔍 Get detailed information about specific effects
- 🎨 Apply effects and presets to your devices with ease
- 🖼️ Manage and switch between different layouts
- 🔆 Control brightness levels
- 🔌 Enable or disable the canvas
- 🖥️ User-friendly command-line interface with intuitive subcommands
- 🐍 Python client libraries for seamless integration:
  - Synchronous API for straightforward scripts
  - Asynchronous API for asyncio-based applications
- 🔐 Robust error handling and connection management
- 🔄 Automatic effect caching for improved performance

## 🚀 Quick Start

### Installation

```bash
pip install signalrgb
```

### Command-Line Interface

List available effects:

```bash
signalrgb effect list
```

Apply a specific effect:

```bash
signalrgb effect apply "Rainbow Wave"
```

### Synchronous Python API

```python
from signalrgb import SignalRGBClient

# Initialize the client
client = SignalRGBClient()

# Apply an effect
client.apply_effect_by_name("Rainbow Wave")

# Control brightness
client.brightness = 75

# Enable/disable the canvas
client.enabled = True

# Get current effect information
effect = client.get_current_effect()
print(f"Current effect: {effect.attributes.name}")
```

### Asynchronous Python API

```python
import asyncio
from signalrgb import AsyncSignalRGBClient

async def main():
    # Use the async client as a context manager
    async with AsyncSignalRGBClient() as client:
        # Apply an effect
        await client.apply_effect_by_name("Rainbow Wave")

        # Control brightness
        await client.set_brightness(75)

        # Get current effect information
        effect = await client.get_current_effect()
        print(f"Current effect: {effect.attributes.name}")

# Run the async code
asyncio.run(main())
```

## 📚 Documentation

- **[Installation](installation.md)** - Detailed installation instructions
- **Usage Guides**:
  - [Command-Line Interface](usage/cli.md) - Using the SignalRGB CLI
  - [Synchronous Library](usage/library.md) - Using the Python library in synchronous code
  - [Asynchronous Library](async_usage.md) - Using the async Python library with asyncio
- **API Reference**:
  - [Client API](api/client.md) - SignalRGBClient reference
  - [Models](api/models.md) - Data model reference
- **Development**:
  - [Contributing](contributing.md) - Guidelines for contributors
  - [Development Guide](development.md) - Setting up your development environment
