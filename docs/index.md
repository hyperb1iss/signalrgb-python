# signalrgb-python

Welcome to the documentation for signalrgb-python. This library provides a powerful and easy-to-use interface for controlling [SignalRGB Pro](https://signalrgb.com) through both a command-line interface (CLI) and a Python library.

## Features

- 📋 List available lighting effects and presets
- 🔍 Get detailed information about specific effects
- 🎨 Apply effects and presets to your devices with ease
- 🖼️ Manage and switch between different layouts
- 🔆 Control brightness levels
- 🔌 Enable or disable the canvas
- 🖥️ User-friendly command-line interface with intuitive subcommands
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
signalrgb effect list
```

Or use the Python library in your code:

```python
from signalrgb.client import SignalRGBClient

client = SignalRGBClient()
effects = client.get_effects()
for effect in effects:
    print(f"Effect: {effect.attributes.name}")

# Control brightness
client.brightness = 75
print(f"Current brightness: {client.brightness}")

# Enable/disable the canvas
client.enabled = True
print(f"Canvas enabled: {client.enabled}")

# List and apply presets
current_effect = client.get_current_effect()
presets = client.get_effect_presets(current_effect.id)
for preset in presets:
    print(f"Preset: {preset.id}")
client.apply_effect_preset(current_effect.id, presets[0].id)

# Manage layouts
layouts = client.get_layouts()
for layout in layouts:
    print(f"Layout: {layout.id}")
client.current_layout = layouts[0].id
```

For more detailed information, check out the [Installation](installation.md) and [Usage](usage/cli.md) guides.
