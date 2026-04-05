# Python Library Usage (Synchronous)

This guide covers the synchronous `SignalRGBClient`. For asyncio-based applications, see the [Async Client guide](../async_usage.md).

## 🎯 Initializing the client

```python
from signalrgb import SignalRGBClient

# Default: localhost:16038
client = SignalRGBClient()

# Or with custom host, port, and timeout
client = SignalRGBClient(host="192.168.1.100", port=16038, timeout=5.0)
```

The client also works as a context manager for clean resource cleanup:

```python
with SignalRGBClient() as client:
    current = client.get_current_effect()
    print(current.attributes.name)
```

## 🎨 Working with effects

### Listing effects

```python
for effect in client.get_effects():
    print(f"{effect.attributes.name} — {effect.attributes.description}")
```

### Getting effect details

```python
# By name
effect = client.get_effect_by_name("Rain")
print(effect.attributes.name, effect.attributes.uses_audio)

# By ID
effect = client.get_effect("effect_id_123")
```

### Applying an effect

```python
client.apply_effect_by_name("Rainbow Wave")
# or
client.apply_effect("effect_id_123")
```

### Current effect

```python
current = client.get_current_effect()
print(current.attributes.name)
```

### Navigation and random

```python
next_effect = client.apply_next_effect()
prev_effect = client.apply_previous_effect()
random_effect = client.apply_random_effect()
```

## 🌊 Working with presets

```python
current = client.get_current_effect()
presets = client.get_effect_presets(current.id)
for preset in presets:
    print(preset.id)

# Apply a preset
client.apply_effect_preset(current.id, "Cool Preset")
```

## 📐 Working with layouts

```python
for layout in client.get_layouts():
    print(layout.id)

# Set the current layout (via property)
client.current_layout = "Gaming Setup"

# Read the current layout
print(client.current_layout.id)
```

## 🎛️ Controlling the canvas

### Brightness

```python
print(client.brightness)    # read (0–100)
client.brightness = 75      # set
```

### Enabled state

```python
print(client.enabled)       # read
client.enabled = True       # enable
client.enabled = False      # disable
```

## 🛡️ Error handling

```python
from signalrgb import SignalRGBClient, ConnectionError, APIError, NotFoundError

client = SignalRGBClient()

try:
    client.apply_effect_by_name("Non-existent Effect")
except ConnectionError as e:
    print(f"Connection failed: {e}")
except NotFoundError as e:
    print(f"Effect not found: {e}")
except APIError as e:
    print(f"API error: {e}")
```

All three exceptions inherit from `SignalRGBError`, so you can also catch the base class.

## 🔄 Cache management

`get_effects()` caches results for performance. Force a refresh:

```python
client.refresh_effects()
effects = client.get_effects()  # fresh fetch
```

## 🔍 Effect parameters

Some effects expose tunable parameters via `effect.attributes.parameters`:

```python
effect = client.get_effect_by_name("Falling Stars")
for name, param in effect.attributes.parameters.items():
    print(f"{name}: type={param.get('type', 'unknown')} value={param.get('value')}")
```

The shape varies per effect — inspect the dict to see what's available.

## 🔄 Using the sync client from async code

Prefer `AsyncSignalRGBClient` for async code. If you must call the sync client from an async context, delegate to a thread pool:

```python
import asyncio
from signalrgb import SignalRGBClient

async def get_effects_async():
    loop = asyncio.get_running_loop()
    client = SignalRGBClient()
    return await loop.run_in_executor(None, client.get_effects)
```

## 📋 Complete example

```python
from signalrgb import SignalRGBClient, ConnectionError, APIError, NotFoundError


def main() -> None:
    try:
        with SignalRGBClient(host="localhost", port=16038) as client:
            # List effects
            for effect in client.get_effects():
                print(f"- {effect.attributes.name}")

            # Apply a specific effect
            effect = client.get_effect_by_name("Rainbow Wave")
            client.apply_effect_by_name(effect.attributes.name)
            print(f"Applied: {effect.attributes.name}")

            # Canvas control
            client.brightness = 75
            client.enabled = True

            # List layouts
            for layout in client.get_layouts():
                print(f"Layout: {layout.id}")

            # Random effect
            random_effect = client.apply_random_effect()
            print(f"Random: {random_effect.attributes.name}")

    except ConnectionError as e:
        print(f"Connection error: {e}")
    except NotFoundError as e:
        print(f"Not found: {e}")
    except APIError as e:
        print(f"API error: {e}")


if __name__ == "__main__":
    main()
```

## 💡 Best practices

1. **Use a context manager** to ensure resources are cleaned up.
2. **Catch specific exceptions** before falling back to `SignalRGBError`.
3. **Refresh the cache** before listing effects when freshness matters.
4. **Throttle requests** in loops — SignalRGB is local but still has overhead.
5. **Prefer the async client** for asyncio apps — it's the primary implementation, and the sync client wraps it.
