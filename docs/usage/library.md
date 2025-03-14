# Python Library Usage

signalrgb-python can be easily integrated into your Python projects. This guide covers the basic usage of the synchronous library. For asyncio-based applications, see the [Async Client Usage](../async_usage.md) guide.

## 🚀 Initializing the Client

First, import the `SignalRGBClient` class and create an instance:

```python
from signalrgb import SignalRGBClient

# Default connection (localhost:16038)
client = SignalRGBClient()

# Or specify custom connection parameters
client = SignalRGBClient(host="192.168.1.100", port=16038, timeout=5.0)
```

The client can also be used as a context manager to ensure proper cleanup of resources:

```python
with SignalRGBClient() as client:
    # Client will be automatically closed when exiting the block
    current_effect = client.get_current_effect()
```

## 🎨 Working with Effects

### Listing Effects

To get a list of all available effects:

```python
effects = client.get_effects()
for effect in effects:
    print(f"Effect: {effect.attributes.name}")
    print(f"Description: {effect.attributes.description}")
```

### Getting Effect Details

To get detailed information about a specific effect:

```python
# By name
effect = client.get_effect_by_name("Rain")
print(f"Effect Name: {effect.attributes.name}")
print(f"Description: {effect.attributes.description}")
print(f"Uses Audio: {effect.attributes.uses_audio}")

# By ID
effect = client.get_effect("effect_id_123")
```

### Applying an Effect

To apply a specific effect:

```python
# By name
client.apply_effect_by_name("Rainbow Wave")

# By ID
client.apply_effect("effect_id_123")
```

### Getting the Current Effect

To see which effect is currently active:

```python
current_effect = client.get_current_effect()
print(f"Current Effect: {current_effect.attributes.name}")
```

### Effect Navigation and Random Effects

Navigate through effects or apply a random effect:

```python
# Apply the next effect in history
next_effect = client.apply_next_effect()
print(f"Applied next effect: {next_effect.attributes.name}")

# Apply the previous effect in history
prev_effect = client.apply_previous_effect()
print(f"Applied previous effect: {prev_effect.attributes.name}")

# Apply a random effect
random_effect = client.apply_random_effect()
print(f"Applied random effect: {random_effect.attributes.name}")
```

## 🌟 Working with Presets

### Listing Presets

To get a list of presets for a specific effect:

```python
effect_id = client.get_current_effect().id
presets = client.get_effect_presets(effect_id)
for preset in presets:
    print(f"Preset: {preset.id}")
```

### Applying a Preset

To apply a preset to the current effect:

```python
effect_id = client.get_current_effect().id
client.apply_effect_preset(effect_id, "Cool Preset")
```

## 📐 Working with Layouts

### Listing Layouts

To get a list of all available layouts:

```python
layouts = client.get_layouts()
for layout in layouts:
    print(f"Layout: {layout.id}")
```

### Setting the Current Layout

To set the current layout:

```python
# Using the property
client.current_layout = "Gaming Setup"

# Check the current layout
print(f"Current Layout: {client.current_layout.id}")
```

## 🎛️ Controlling the Canvas

### Brightness Control

The brightness level can be adjusted from 0 to 100:

```python
# Get current brightness
brightness = client.brightness
print(f"Current brightness: {brightness}")

# Set brightness to 75%
client.brightness = 75
print(f"Brightness set to: {client.brightness}")
```

### Enabling/Disabling the Canvas

To control the enabled state of the canvas:

```python
# Get current state
enabled = client.enabled
print(f"Canvas enabled: {enabled}")

# Enable the canvas
client.enabled = True
print(f"Canvas enabled: {client.enabled}")

# Disable the canvas
client.enabled = False
print(f"Canvas disabled: {client.enabled}")
```

## 🛡️ Error Handling

The client provides custom exceptions for different types of errors. You can handle these exceptions to provide better error messages or implement retry logic:

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
    print(f"API error occurred: {e}")
```

## 🔄 Cache Management

The client caches the list of effects for performance. If you need to refresh this cache:

```python
client.refresh_effects()
effects = client.get_effects()  # Will fetch the latest effects
```

## 🔍 Working with Effect Parameters

Some effects have parameters that can be adjusted. You can access these parameters by examining the effect's attributes:

```python
effect = client.get_effect_by_name("Falling Stars")
parameters = effect.attributes.parameters

# Print all parameters
for param_name, param_data in parameters.items():
    print(f"Parameter: {param_name}")
    print(f"  Type: {param_data.get('type', 'Unknown')}")
    print(f"  Value: {param_data.get('value')}")
```

Note that the structure of parameters can vary between effects. Always check the specific effect's parameters to understand what options are available.

## 🔄 Using the Synchronous Client from Async Code

If you have mostly async code but need to use the synchronous client in a few places, wrap the client methods in async functions:

```python
import asyncio
from signalrgb import SignalRGBClient

async def get_effects_async():
    # Run the synchronous client in a thread pool
    loop = asyncio.get_running_loop()
    client = SignalRGBClient()

    return await loop.run_in_executor(
        None, client.get_effects
    )

# Use it in async code
async def main():
    effects = await get_effects_async()
    print(f"Found {len(effects)} effects")

# Or consider using the AsyncSignalRGBClient instead
```

However, for proper async applications, it's recommended to use the `AsyncSignalRGBClient` directly as shown in the [Async Client Usage](../async_usage.md) guide.

## 📋 Complete Example

Here's a more comprehensive example that demonstrates various features of the signalrgb-python library:

```python
from signalrgb import SignalRGBClient, ConnectionError, APIError, NotFoundError

def main():
    try:
        # Initialize the client
        client = SignalRGBClient(host="localhost", port=16038)

        # List all effects
        print("Available effects:")
        effects = client.get_effects()
        for effect in effects:
            print(f"- {effect.attributes.name}")

        # Get details of a specific effect
        effect_name = "Rainbow Wave"
        effect = client.get_effect_by_name(effect_name)
        print(f"\nDetails of '{effect_name}':")
        print(f"Description: {effect.attributes.description}")
        print(f"Uses Audio: {effect.attributes.uses_audio}")

        # Apply the effect
        client.apply_effect_by_name(effect_name)
        print(f"\nApplied effect: {effect_name}")

        # Get current effect
        current_effect = client.get_current_effect()
        print(f"Current effect: {current_effect.attributes.name}")

        # Adjust brightness
        client.brightness = 75
        print(f"Brightness set to: {client.brightness}")

        # Enable/disable the canvas
        client.enabled = True
        print(f"Canvas enabled: {client.enabled}")

        # List layouts
        layouts = client.get_layouts()
        print("\nAvailable layouts:")
        for layout in layouts:
            print(f"- {layout.id}")

        # Apply a random effect
        random_effect = client.apply_random_effect()
        print(f"\nApplied random effect: {random_effect.attributes.name}")

    except ConnectionError as e:
        print(f"Connection error: {e}")
    except NotFoundError as e:
        print(f"Resource not found: {e}")
    except APIError as e:
        print(f"API error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
```

## 💡 Best Practices

1. **Error Handling**: Always wrap your code in try-except blocks to handle potential errors gracefully.

2. **Resource Management**: Use the client as a context manager when possible to ensure proper cleanup.

3. **Caching**: The `get_effects()` method uses caching to improve performance. If you need the most up-to-date list, call `refresh_effects()` first.

4. **Rate Limiting**: Be mindful of how frequently you're making requests, especially in loops or automated scripts.

5. **Async Support**: For asyncio-based applications, consider using the `AsyncSignalRGBClient` instead.
