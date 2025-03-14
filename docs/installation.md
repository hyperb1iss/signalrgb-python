# Installation

## 🧰 Prerequisites

Before installing signalrgb-python, ensure you have the following:

- Python 3.9 or higher
- [SignalRGB Pro](https://www.signalrgb.com/pro/) (required for API access)

This library uses the [SignalRGB REST API](https://docs.signalrgb.com/signalrgb-api), which is only available in SignalRGB Pro.

### Additional Requirements for Async Usage

To use the asynchronous client (`AsyncSignalRGBClient`), you will need:

- Python 3.9 or higher (same as above)
- Basic understanding of Python's asyncio framework
- For integration with other async frameworks (like Home Assistant), see the [Async Usage](async_usage.md) guide

## 📦 Installing with pip

The easiest way to install signalrgb-python is using pip:

```bash
pip install signalrgb
```

## 🚀 Installing with UV

For faster, more reliable dependency resolution, you can use [UV](https://github.com/astral-sh/uv) to install signalrgb-python:

```bash
# Install UV if you don't have it already
pip install uv

# Install signalrgb using UV
uv pip install signalrgb
```

## 🔧 Development Installation

If you're working on signalrgb-python development, you can install it with development dependencies:

```bash
# Clone the repository
git clone https://github.com/hyperb1iss/signalrgb-python.git
cd signalrgb-python

# Using UV
uv sync --groups dev
```

## ✅ Verifying the Installation

After installation, you can verify that signalrgb-python is correctly installed by running:

```bash
signalrgb --version
```

This should display the version number of the installed client.

You can also verify the Python library is working by importing it in a Python shell:

```python
import signalrgb
print(signalrgb.__version__)
```

## 📚 Next Steps

Now that you have installed signalrgb-python, you can start using it:

- [CLI Usage](usage/cli.md) - Learn how to use the command-line interface
- [Python Library Usage](usage/library.md) - Learn how to use the synchronous Python library
- [Async Library Usage](async_usage.md) - Learn how to use the asynchronous Python library
