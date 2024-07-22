# 🌈 signalrgb-python

<div align="center">

[![CI/CD](https://github.com/hyperb1iss/signalrgb-python/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/hyperb1iss/signalrgb-python/actions)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyPI version](https://badge.fury.io/py/signalrgb.svg)](https://badge.fury.io/py/signalrgb)

*A powerful Python client library and CLI for controlling [SignalRGB Pro](https://signalrgb.com)*

[Features](#✨-features) • [Installation](#💻-installation) • [Usage](#🚀-usage) • [API Reference](#📘-api-reference) • [Development](#🛠️-development) • [Contributing](#👥-contributing) • [License](#📄-license)

</div>

## ✨ Features

- 📋 List available lighting effects
- 🔍 Get detailed information about specific effects
- 🎨 Apply effects to your devices with ease
- 🖥️ User-friendly command-line interface
- 🐍 Python client library for seamless integration into your projects
- 🔐 Error handling and connection management
- 🔄 Automatic effect caching for improved performance

## 💻 Installation

You can install signalrgb-python using pip:

```bash
pip install signalrgb
```

Or if you prefer to use Poetry:

```bash
poetry add signalrgb
```

### Prerequisites

- Python 3.12 or higher
- [SignalRGB Pro](https://www.signalrgb.com/pro/) (required for API access)

This library uses the [SignalRGB REST API](https://docs.signalrgb.com/signalrgb-api), which is only available in SignalRGB Pro.

## 🚀 Usage

### Command-line Interface

signalrgb-python comes with an intuitive command-line interface for easy interaction with your SignalRGB setup.

```bash
# List all available effects
signalrgb list-effects

# Get details of a specific effect
signalrgb get-effect "Psychedelic Dream"

# Apply an effect
signalrgb apply-effect "Rave Visualizer"

# Get the current effect
signalrgb current-effect
```

You can also specify a custom host and port:

```bash
signalrgb --host hyperia.home --port 16038 list-effects
```

For a full list of available commands and options, use:

```bash
signalrgb --help
```

### Python Library

Integrate signalrgb-python into your own Python projects with ease:

```python
from signalrgb.client import SignalRGBClient

# Initialize the client
client = SignalRGBClient(host="hyperia.home", port=16038)

# List all effects
effects = client.get_effects()
for effect in effects:
    print(f"Effect: {effect.attributes.name}")

# Apply an effect
client.apply_effect_by_name("Rain")

# Get current effect
current_effect = client.get_current_effect()
print(f"Current effect: {current_effect.attributes.name}")
```

### Error Handling

The client provides custom exceptions for different types of errors:

```python
from signalrgb.client import SignalRGBClient, ConnectionError, APIError, EffectNotFoundError

client = SignalRGBClient()

try:
    client.apply_effect_by_name("Non-existent Effect")
except ConnectionError as e:
    print(f"Connection failed: {e}")
except EffectNotFoundError as e:
    print(f"Effect not found: {e}")
except APIError as e:
    print(f"API error occurred: {e}")
```

## 📘 API Reference

For detailed information about the available methods and classes, please refer to our [API Documentation](https://hyperb1iss.github.io/signalrgb-python/).

## 🛠️ Development

To set up the development environment:

1. Clone the repository:
   ```bash
   git clone https://github.com/hyperb1iss/signalrgb-python.git
   cd signalrgb-python
   ```
2. Install Poetry if you haven't already: `pip install poetry`
3. Install dependencies: `poetry install`
4. Activate the virtual environment: `poetry shell`

To run tests:

```bash
pytest
```

Check out our [Development Guide](https://hyperb1iss.github.io/signalrgb-python/development/) for more information!

## 👥 Contributing

Have a fix or new feature that you want to add? That's amazing! You're amazing!

1. Fork the repository
2. Create a new branch: `git checkout -b feature-branch-name`
3. Make your changes and commit them: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-branch-name`
5. Submit a pull request

Please make sure to update tests as appropriate and adhere to the project's coding standards.

## 📄 License

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

If you find this project helpful, consider [buying me a coffee](https://ko-fi.com/hyperb1iss)! ☕

</div>
