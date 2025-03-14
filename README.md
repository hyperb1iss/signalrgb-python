# 🌈 signalrgb-python

<div align="center">

[![CI/CD](https://github.com/hyperb1iss/signalrgb-python/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/hyperb1iss/signalrgb-python/actions)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyPI version](https://img.shields.io/pypi/v/signalrgb)](https://pypi.org/project/signalrgb)

_A powerful Python client library and CLI for controlling [SignalRGB Pro](https://signalrgb.com)_

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [API Reference](#api-reference) • [Development](#development) • [Contributing](#contributing) • [License](#license)

</div>

## ✨ Features

<a name="features"></a>

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
- ⚡ Native asyncio support for async applications and integrations

## 💻 Installation

<a name="installation"></a>

You can install signalrgb-python using pip:

```bash
pip install signalrgb
```

Or if you prefer to use [uv](https://github.com/astral-sh/uv):

```bash
uv add signalrgb
```

### Prerequisites

- Python 3.11 or higher
- [SignalRGB Pro](https://www.signalrgb.com/pro/) (required for API access)

This library uses the [SignalRGB REST API](https://docs.signalrgb.com/signalrgb-api), which is only available in SignalRGB Pro.

## 🚀 Usage

<a name="usage"></a>

### Command-line Interface

signalrgb-python comes with an intuitive command-line interface for easy interaction with your SignalRGB setup. The CLI now uses a subcommand structure for better organization and extensibility.

```bash
# List all available effects
signalrgb effect list

# Get details of a specific effect
signalrgb effect "Psychedelic Dream"

# Apply an effect
signalrgb effect apply "Rave Visualizer"

# List presets for the current effect
signalrgb preset list

# Apply a preset to the current effect
signalrgb preset apply "My Fancy Preset"

# List available layouts
signalrgb layout list

# Set the current layout
signalrgb layout set "My Gaming Layout"

# Get the current effect
signalrgb effect

# Set brightness level (0-100)
signalrgb canvas brightness 75

# Get current brightness level
signalrgb canvas brightness

# Enable the canvas
signalrgb canvas enable

# Disable the canvas
signalrgb canvas disable
```

You can also specify a custom host and port:

```bash
signalrgb --host hyperia.home --port 16038 effect list
```

For a full list of available commands and options, use:

```bash
signalrgb --help
```

### Python Library

#### Synchronous API

Integrate signalrgb-python into your own Python projects with ease:

```python
from signalrgb import SignalRGBClient

# Initialize the client
client = SignalRGBClient(host="hyperia.home", port=16038)

# List all effects
effects = client.get_effects()
for effect in effects:
    print(f"Effect: {effect.attributes.name}")

# Apply an effect
client.apply_effect_by_name("Rain")

# List presets for the current effect
current_effect = client.get_current_effect()
presets = client.get_effect_presets(current_effect.id)
for preset in presets:
    print(f"Preset: {preset.id}")

# Apply a preset
client.apply_effect_preset(current_effect.id, "Cool Preset")

# Get available layouts
layouts = client.get_layouts()
for layout in layouts:
    print(f"Layout: {layout.id}")

# Set the current layout
client.current_layout = "Gaming Setup"

# Control brightness
client.brightness = 50
print(f"Current brightness: {client.brightness}")

# Enable/disable the canvas
client.enabled = True
print(f"Canvas enabled: {client.enabled}")
```

#### Asynchronous API ⚡

For async applications like Home Assistant integrations, use the async API:

```python
import asyncio
from signalrgb import AsyncSignalRGBClient

async def main():
    # Initialize the client with context manager for auto-cleanup
    async with AsyncSignalRGBClient(host="hyperia.home", port=16038) as client:
        # List all effects
        effects = await client.get_effects()
        for effect in effects:
            print(f"Effect: {effect.attributes.name}")

        # Apply an effect
        await client.apply_effect_by_name("Rain")

        # Get and update brightness
        brightness = await client.get_brightness()
        print(f"Current brightness: {brightness}")
        await client.set_brightness(75)

        # Enable/disable the canvas
        is_enabled = await client.get_enabled()
        print(f"Canvas enabled: {is_enabled}")
        await client.set_enabled(True)

        # Get current effect
        current = await client.get_current_effect()
        print(f"Current effect: {current.attributes.name}")

# Run the async function
asyncio.run(main())
```

For more details on the async API, see [docs/async_usage.md](docs/async_usage.md).

### Error Handling

The client provides custom exceptions for different types of errors:

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
    print(f"API error occurred: {e}")
```

The same error handling pattern works for the async client too.

## 📘 API Reference

<a name="api-reference"></a>

For detailed information about the available methods and classes, please refer to our [API Documentation](https://hyperb1iss.github.io/signalrgb-python/).

## 🛠️ Development

<a name="development"></a>

To set up the development environment:

1. Clone the repository:
   ```bash
   git clone https://github.com/hyperb1iss/signalrgb-python.git
   cd signalrgb-python
   ```
2. Install [uv](https://github.com/astral-sh/uv) if you haven't already
3. Install dependencies: `uv sync`
4. Activate a virtual environment if needed: `uv venv .venv && . .venv/bin/activate`

To run tests:

```bash
pytest
```

Check out our [Development Guide](https://hyperb1iss.github.io/signalrgb-python/development/) for more information!

## 👥 Contributing

<a name="contributing"></a>

Have a fix or new feature that you want to add? That's amazing! You're amazing!

1. Fork the repository
2. Create a new branch: `git checkout -b feature-branch-name`
3. Make your changes and commit them: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-branch-name`
5. Submit a pull request

Please make sure to update tests as appropriate and adhere to the project's coding standards.

## 📄 License

<a name="license"></a>

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

---

<div align="center">

📚 [Documentation](https://hyperb1iss.github.io/signalrgb-python/) • 🐛 [Report Bug](https://github.com/hyperb1iss/signalrgb-python/issues) • 💡 [Request Feature](https://github.com/hyperb1iss/signalrgb-python/issues)

</div>

## 🙏 Acknowledgements

This project is not officially associated with SignalRGB. It's an independent client library created by the community for the community. Please do not report issues related to this client to the SignalRGB team.

---

<div align="center">

Created by [Stefanie Jane 🌠](https://github.com/hyperb1iss)

If you find this project useful, consider [buying me a Monster Ultra Violet!](https://ko-fi.com/hyperb1iss)! ⚡️

</div>
