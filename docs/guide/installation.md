# Installation

## With uv (recommended)

```bash
# Add to a uv project
uv add signalrgb

# Or install as a standalone CLI tool
uv tool install signalrgb
```

## With pip

```bash
pip install signalrgb
```

## Development setup

```bash
git clone https://github.com/hyperb1iss/signalrgb-python.git
cd signalrgb-python

# Install runtime + dev + docs
just install       # or: uv sync --all-groups
```

## Verify

```bash
signalrgb --help
```

```python
import signalrgb
print(signalrgb.__version__)
```
