# Using the Async SignalRGB Client

Starting from version 1.0.0, signalrgb-python includes a native asyncio-based client that allows you to integrate SignalRGB functionality with async code.

## Basic Usage

```python
import asyncio
from signalrgb import AsyncSignalRGBClient

async def main():
    # Create a client
    async with AsyncSignalRGBClient() as client:
        # Get current effect
        effect = await client.get_current_effect()
        print(f"Current effect: {effect.attributes.name}")

        # List available effects
        effects = await client.get_effects()
        print(f"Available effects: {len(effects)}")

        # Apply a random effect
        new_effect = await client.apply_random_effect()
        print(f"Applied effect: {new_effect.attributes.name}")

# Run the async code
asyncio.run(main())
```

## Comparison with Synchronous Client

The async client provides the same functionality as the synchronous client but with async/await syntax:

| Synchronous Client        | Asynchronous Client               |
| ------------------------- | --------------------------------- |
| `client.get_effects()`    | `await client.get_effects()`      |
| `client.apply_effect(id)` | `await client.apply_effect(id)`   |
| `client.brightness = 50`  | `await client.set_brightness(50)` |
| `client.enabled = True`   | `await client.set_enabled(True)`  |

## Properties vs Methods

Unlike the synchronous client, the asynchronous client doesn't use properties for read/write operations because properties in Python can't be async. Instead:

- `client.brightness` → `await client.get_brightness()`
- `client.brightness = 50` → `await client.set_brightness(50)`
- `client.enabled` → `await client.get_enabled()`
- `client.enabled = True` → `await client.set_enabled(True)`
- `client.current_layout` → `await client.get_current_layout()`
- `client.current_layout = "layout1"` → `await client.set_current_layout("layout1")`

## Integration with Home Assistant

The async client is particularly well-suited for integrating with Home Assistant, which uses asyncio for its operations:

```python
from homeassistant.components.light import LightEntity
from signalrgb import AsyncSignalRGBClient

class SignalRGBLight(LightEntity):
    def __init__(self, client):
        self._client = client
        self._name = "SignalRGB"
        self._state = False
        self._brightness = 0

    async def async_turn_on(self, **kwargs):
        await self._client.set_enabled(True)
        self._state = True

    async def async_turn_off(self, **kwargs):
        await self._client.set_enabled(False)
        self._state = False

    async def async_update(self):
        self._state = await self._client.get_enabled()
        self._brightness = await self._client.get_brightness()
```

See the `examples/home_assistant_example.py` file for a more complete Home Assistant integration example.

## Context Manager Support

The async client supports being used as an async context manager:

```python
async with AsyncSignalRGBClient() as client:
    # client is automatically closed when exiting this block
    await client.get_effects()
```

This ensures proper cleanup of resources when the client is no longer needed.

## Error Handling

The async client raises the same exceptions as the synchronous client:

```python
try:
    await client.apply_effect("nonexistent_effect")
except NotFoundError:
    print("Effect not found")
except ConnectionError:
    print("Connection error")
except APIError as e:
    print(f"API error: {e}")
```

## Backward Compatibility

The synchronous client is still available and fully functional. In fact, it now uses the async client internally, running operations in a synchronized manner. This allows existing code to continue working without changes.

If you're using the client in a synchronous context but need to call it from async code in some places, you can mix approaches:

```python
# Synchronous code
from signalrgb import SignalRGBClient

client = SignalRGBClient()
effects = client.get_effects()

# Later, in an async context
async def async_function():
    # Use the async client directly
    async with AsyncSignalRGBClient() as async_client:
        await async_client.apply_effect("some_effect")
```

## Performance Considerations

The async client can offer better performance in async applications, especially when making multiple requests or when integrating with other async code like Home Assistant. It avoids blocking the event loop while waiting for API responses.
