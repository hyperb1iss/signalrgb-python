# SignalRGB Client API Reference

This page provides detailed API documentation for the `SignalRGBClient` class, which is the main interface for interacting with the SignalRGB API.

## SignalRGBClient

::: signalrgb.client.SignalRGBClient
    options:
      show_root_heading: true
      show_source: true

## Exceptions

The SignalRGB client defines several custom exceptions for error handling:

::: signalrgb.client.SignalRGBException
    options:
      show_root_heading: true
      show_source: true

::: signalrgb.client.ConnectionError
    options:
      show_root_heading: true
      show_source: true

::: signalrgb.client.APIError
    options:
      show_root_heading: true
      show_source: true

::: signalrgb.client.NotFoundError
    options:
      show_root_heading: true
      show_source: true

## Usage Example

Here's a basic example of how to use the SignalRGBClient:

```python
from signalrgb import SignalRGBClient

# Initialize the client
client = SignalRGBClient(host="localhost", port=16038)

# Get all effects
effects = client.get_effects()
for effect in effects:
    print(f"Effect: {effect.attributes.name}")

# Apply an effect
client.apply_effect_by_name("Rainbow Wave")

# Get current effect
current_effect = client.get_current_effect()
print(f"Current effect: {current_effect.attributes.name}")
```

For more detailed usage examples, please refer to the [Python Library Usage](../usage/library.md) guide.
