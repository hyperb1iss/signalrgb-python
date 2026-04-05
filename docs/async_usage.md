# Asynchronous Client

`AsyncSignalRGBClient` is the native asyncio client for signalrgb-python. It's built on httpx and is particularly useful for Home Assistant integrations and other async applications.

Since version 1.0.0, the async client is the **primary** implementation — the synchronous `SignalRGBClient` wraps it behind a blocking event loop.

## 🎯 Basic usage

```python
import asyncio
from signalrgb import AsyncSignalRGBClient

async def main() -> None:
    async with AsyncSignalRGBClient() as client:
        # Current effect
        effect = await client.get_current_effect()
        print(f"Current: {effect.attributes.name}")

        # List effects
        effects = await client.get_effects()
        print(f"Available: {len(effects)}")

        # Apply a random effect
        new_effect = await client.apply_random_effect()
        print(f"Applied: {new_effect.attributes.name}")

asyncio.run(main())
```

## 📊 Sync vs async — side by side

| Synchronous                    | Asynchronous                          |
| ------------------------------ | ------------------------------------- |
| `client.get_effects()`         | `await client.get_effects()`          |
| `client.apply_effect(id)`      | `await client.apply_effect(id)`       |
| `client.brightness = 50`       | `await client.set_brightness(50)`     |
| `client.enabled = True`        | `await client.set_enabled(True)`      |

## 🔄 Properties vs methods

Properties can't be async in Python, so the async client uses explicit getter and setter methods:

| Synchronous                        | Asynchronous                                |
| ---------------------------------- | ------------------------------------------- |
| `client.brightness`                | `await client.get_brightness()`             |
| `client.brightness = 50`           | `await client.set_brightness(50)`           |
| `client.enabled`                   | `await client.get_enabled()`                |
| `client.enabled = True`            | `await client.set_enabled(True)`            |
| `client.current_layout`            | `await client.get_current_layout()`         |
| `client.current_layout = "layout"` | `await client.set_current_layout("layout")` |

## 🏠 Home Assistant integration

The async client is a natural fit for Home Assistant. See [signalrgb-homeassistant](https://github.com/hyperb1iss/signalrgb-homeassistant) for the full integration; here's a minimal `LightEntity`:

```python
from homeassistant.components.light import LightEntity
from signalrgb import AsyncSignalRGBClient


class SignalRGBLight(LightEntity):
    def __init__(self, client: AsyncSignalRGBClient) -> None:
        self._client = client
        self._state = False
        self._brightness = 0

    async def async_turn_on(self, **kwargs) -> None:
        await self._client.set_enabled(True)
        if "brightness" in kwargs:
            # HA brightness is 0–255, SignalRGB is 0–100
            await self._client.set_brightness(round(kwargs["brightness"] / 255 * 100))
        self._state = True

    async def async_turn_off(self, **kwargs) -> None:
        await self._client.set_enabled(False)
        self._state = False

    async def async_update(self) -> None:
        self._state = await self._client.get_enabled()
        self._brightness = await self._client.get_brightness()
```

## 📦 Context manager support

Use the client as an async context manager for automatic cleanup:

```python
async with AsyncSignalRGBClient() as client:
    await client.get_effects()
# client.aclose() called automatically here
```

Or manage it manually:

```python
client = AsyncSignalRGBClient()
try:
    await client.get_effects()
finally:
    await client.aclose()
```

## 🛡️ Error handling

The async client raises the same exceptions as the synchronous one:

```python
from signalrgb import AsyncSignalRGBClient, ConnectionError, APIError, NotFoundError

async with AsyncSignalRGBClient() as client:
    try:
        await client.apply_effect_by_name("nonexistent")
    except NotFoundError:
        print("Effect not found")
    except ConnectionError:
        print("Connection error")
    except APIError as e:
        print(f"API error: {e}")
```

## 🔄 Mixing sync and async code

If most of your code is sync but a few paths need async, the cleanest approach is to use `AsyncSignalRGBClient` directly in those paths:

```python
from signalrgb import SignalRGBClient, AsyncSignalRGBClient

# Synchronous code
client = SignalRGBClient()
effects = client.get_effects()

# Async code
async def async_function():
    async with AsyncSignalRGBClient() as async_client:
        await async_client.apply_effect_by_name("some_effect")
```

## 🎯 Performance considerations

The async client avoids blocking the event loop while waiting for API responses. That's particularly valuable when:

- Making multiple concurrent requests (`asyncio.gather`)
- Integrating with other async code (Home Assistant, aiohttp servers, etc.)
- Processing many effects or devices in parallel
- Building responsive event-loop-based applications

## 💡 Advanced example: effect cycling

Cycle through every available effect, displaying each for a configurable duration:

```python
import asyncio
from signalrgb import AsyncSignalRGBClient


async def cycle_effects(duration: float = 5) -> None:
    async with AsyncSignalRGBClient() as client:
        effects = await client.get_effects()
        print(f"Cycling through {len(effects)} effects...")

        for effect in effects:
            print(f"→ {effect.attributes.name}")
            await client.apply_effect(effect.id)
            await asyncio.sleep(duration)


if __name__ == "__main__":
    asyncio.run(cycle_effects(duration=3))
```
