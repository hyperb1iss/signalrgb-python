# 🌈 SignalRGB Python Client

<div align="center">

[![CircleCI](https://dl.circleci.com/status-badge/img/circleci/HnjwXsMN4bebM2B2r69BKp/A9i1RqBjrUCp2Prq5brJgh/tree/main.svg?style=shield&circle-token=CCIPRJ_3zJ7eJJi16hxx8JGuNxZtP_907df1eecb62b96f7dbc93bdd9c239d0cd4674c6)](https://dl.circleci.com/status-badge/redirect/circleci/HnjwXsMN4bebM2B2r69BKp/A9i1RqBjrUCp2Prq5brJgh/tree/main)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyPI version](https://badge.fury.io/py/signalrgb.svg)](https://badge.fury.io/py/signalrgb)

*A powerful Python client library and CLI for controlling [SignalRGB](https://signalrgb.com)*

[Features](#✨-features) • [Installation](#💻-installation) • [Usage](#🚀-usage) • [Development](#🛠️-development) • [Contributing](#👥-contributing) • [License](#📄-license)

</div>

## ✨ Features

- 📋 List available lighting effects
- 🔍 Get detailed information about specific effects
- 🎨 Apply effects to your devices with ease
- 🖥️ User-friendly command-line interface
- 🐍 Python client library for seamless integration into your projects

## 💻 Installation

You can install the SignalRGB Python Client using pip:

```bash
pip install signalrgb
```

Or if you prefer to use Poetry:

```bash
poetry add signalrgb
```

## 🚀 Usage

### Command-line Interface

The SignalRGB Python Client comes with an intuitive command-line interface for easy interaction with your SignalRGB setup.

```bash
# List all available effects
signalrgb list-effects

# Get details of a specific effect
signalrgb get-effect "Rainbow Wave"

# Apply an effect
signalrgb apply-effect "Audio Visualizer"

# Get the current effect
signalrgb current-effect
```

You can also specify a custom host and port:

```bash
signalrgb --host hyperia.home --port 16038 list-effects
```

### Python Library

Integrate the SignalRGB Python Client into your own Python projects with ease:

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

# Get current effect
current_effect = client.get_current_effect()
print(f"Current effect: {current_effect.attributes.name}")
```

## 🛠️ Development

To set up the development environment:

1. Clone the repository
2. Install Poetry if you haven't already: `pip install poetry`
3. Install dependencies: `poetry install`
4. Activate the virtual environment: `poetry shell`

To run tests:

```bash
pytest
```

## 👥 Contributing

Got a fix or a new feature? Congratulations: You're awesome!

1. Fork the repository
2. Create a new branch: `git checkout -b feature-branch-name`
3. Make your changes and commit them: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-branch-name`
5. Submit a pull request


## 📄 License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

---

<div align="center">

📚 **Documentation** • 🐛 [Report Bug](https://github.com/hyperb1iss/signalrgb-python/issues) • 💡 [Request Feature](https://github.com/hyperb1iss/signalrgb-python/issues)

</div>

## 🙏 Acknowledgements

This project is not officially associated with SignalRGB- it's an independent client library created by the community. Do not report issues to the SignalRGB team!

---
<div align="center">

Created by [Stefanie Jane 🌠](https://github.com/hyperb1iss)

</div>

