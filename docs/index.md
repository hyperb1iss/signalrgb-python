# signalrgb-python

Welcome to the documentation for signalrgb-python. This library provides a powerful and easy-to-use interface for controlling [SignalRGB Pro](https://signalrgb.com) through both a command-line interface (CLI) and a Python library.

## Features

- 📋 List available lighting effects
- 🔍 Get detailed information about specific effects
- 🎨 Apply effects to your devices with ease
- 🖥️ User-friendly command-line interface
- 🐍 Python client library for seamless integration into your projects
- 🔐 Error handling and connection management
- 🔄 Automatic effect caching for improved performance

## Quick Start

Install signalrgb-python:

```bash
pip install signalrgb
```

Use the CLI to list available effects:

```bash
signalrgb list-effects
```

Or use the Python library in your code:

```python
from signalrgb.client import SignalRGBClient

client = SignalRGBClient()
effects = client.get_effects()
for effect in effects:
    print(f"Effect: {effect.attributes.name}")
```

For more detailed information, check out the [Installation](installation.md) and [Usage](usage/cli.md) guides.
