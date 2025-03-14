# SignalRGB Client API Reference

This page provides detailed API documentation for both the synchronous `SignalRGBClient` class and the asynchronous `AsyncSignalRGBClient` class, which are the main interfaces for interacting with the SignalRGB API.

## SignalRGBClient

::: signalrgb.client.SignalRGBClient
    options:
      show_root_heading: true
      show_source: true

## AsyncSignalRGBClient

::: signalrgb.async_client.AsyncSignalRGBClient
    options:
      show_root_heading: true
      show_source: true

## Exceptions

The SignalRGB client defines several custom exceptions for error handling:

::: signalrgb.exceptions.SignalRGBException
    options:
      show_root_heading: true
      show_source: true

::: signalrgb.exceptions.ConnectionError
    options:
      show_root_heading: true
      show_source: true

::: signalrgb.exceptions.APIError
    options:
      show_root_heading: true
      show_source: true

::: signalrgb.exceptions.NotFoundError
    options:
      show_root_heading: true
      show_source: true

## Usage Examples

### Synchronous Client Example

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

# Adjust brightness
client.brightness = 75
print(f"Brightness set to: {client.brightness}")
```

### Asynchronous Client Example

```python
import asyncio
from signalrgb import AsyncSignalRGBClient

async def main():
    # Initialize the client using a context manager
    async with AsyncSignalRGBClient(host="localhost", port=16038) as client:
        # Get all effects
        effects = await client.get_effects()
        for effect in effects:
            print(f"Effect: {effect.attributes.name}")
        
        # Apply an effect
        await client.apply_effect_by_name("Rainbow Wave")
        
        # Get current effect
        current_effect = await client.get_current_effect()
        print(f"Current effect: {current_effect.attributes.name}")
        
        # Adjust brightness
        await client.set_brightness(75)
        brightness = await client.get_brightness()
        print(f"Brightness set to: {brightness}")

# Run the async example
asyncio.run(main())
```

For more detailed usage examples, please refer to:
- [Python Library Usage](../usage/library.md) for the synchronous client
- [Asynchronous Library Usage](../async_usage.md) for the async client
