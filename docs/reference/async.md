# Async Client

`AsyncSignalRGBClient` is the native httpx async client — the primary implementation that the sync
client wraps. Use it for asyncio applications and Home Assistant integrations.

## Constructor

```python
from signalrgb import AsyncSignalRGBClient

client = AsyncSignalRGBClient(
    host="localhost",
    port=16038,
    timeout=10.0,
)
```

## Context manager

```python
async with AsyncSignalRGBClient() as client:
    effect = await client.get_current_effect()
    print(effect.attributes.name)
# aclose() called automatically
```

Or manual cleanup:

```python
client = AsyncSignalRGBClient()
try:
    await client.get_effects()
finally:
    await client.aclose()
```

## Sync vs async API

The async client uses explicit methods instead of properties (properties can't be async):

| Sync property                 | Async method                           |
| ----------------------------- | -------------------------------------- |
| `client.brightness`           | `await client.get_brightness()`        |
| `client.brightness = 50`      | `await client.set_brightness(50)`      |
| `client.enabled`              | `await client.get_enabled()`           |
| `client.enabled = True`       | `await client.set_enabled(True)`       |
| `client.current_layout`       | `await client.get_current_layout()`    |
| `client.current_layout = "x"` | `await client.set_current_layout("x")` |

## Effects

| Method                             | Returns        |
| ---------------------------------- | -------------- |
| `await get_effects()`              | `list[Effect]` |
| `await get_effect(id)`             | `Effect`       |
| `await get_effect_by_name(name)`   | `Effect`       |
| `await get_current_effect()`       | `Effect`       |
| `await apply_effect(id)`           | `None`         |
| `await apply_effect_by_name(name)` | `None`         |
| `await apply_next_effect()`        | `Effect`       |
| `await apply_previous_effect()`    | `Effect`       |
| `await apply_random_effect()`      | `Effect`       |
| `await refresh_effects()`          | `None`         |

## Presets

| Method                                            | Returns              |
| ------------------------------------------------- | -------------------- |
| `await get_effect_presets(effect_id)`             | `list[EffectPreset]` |
| `await apply_effect_preset(effect_id, preset_id)` | `None`               |

## Layouts

| Method                         | Returns        |
| ------------------------------ | -------------- |
| `await get_layouts()`          | `list[Layout]` |
| `await get_current_layout()`   | `Layout`       |
| `await set_current_layout(id)` | `None`         |

## Home Assistant example

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
            await self._client.set_brightness(
                round(kwargs["brightness"] / 255 * 100)
            )
        self._state = True

    async def async_turn_off(self, **kwargs) -> None:
        await self._client.set_enabled(False)
        self._state = False

    async def async_update(self) -> None:
        self._state = await self._client.get_enabled()
        self._brightness = await self._client.get_brightness()
```

See [signalrgb-homeassistant](https://github.com/hyperb1iss/signalrgb-homeassistant) for the full
integration.
