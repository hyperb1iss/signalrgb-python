# Quick Start

## CLI

```bash
# List effects
signalrgb effect list

# Apply an effect
signalrgb effect apply "Rainbow Wave"

# Canvas control
signalrgb canvas brightness 75
signalrgb canvas enable

# Point at a remote host
signalrgb --host hyperia.home effect list
```

## Synchronous client

```python
from signalrgb import SignalRGBClient

client = SignalRGBClient()

# List and apply effects
for effect in client.get_effects():
    print(effect.attributes.name)

client.apply_effect_by_name("Rain")

# Canvas control
client.brightness = 75
client.enabled = True
```

## Async client

```python
import asyncio
from signalrgb import AsyncSignalRGBClient

async def main() -> None:
    async with AsyncSignalRGBClient() as client:
        effects = await client.get_effects()
        print(f"Found {len(effects)} effects")

        await client.apply_effect_by_name("Rain")
        await client.set_brightness(75)

asyncio.run(main())
```

## Error handling

```python
from signalrgb import SignalRGBClient, ConnectionError, APIError, NotFoundError

client = SignalRGBClient()

try:
    client.apply_effect_by_name("Nonexistent")
except ConnectionError as e:
    print(f"Connection failed: {e}")
except NotFoundError as e:
    print(f"Not found: {e}")
except APIError as e:
    print(f"API error: {e}")
```

All three inherit from `SignalRGBError`.
