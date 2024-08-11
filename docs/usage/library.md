# Python Library Usage

signalrgb-python can be easily integrated into your Python projects. This guide covers the basic usage of the library.

## Initializing the Client

First, import the `SignalRGBClient` class and create an instance:

```python
from signalrgb import SignalRGBClient

client = SignalRGBClient(host="localhost", port=16038)
```

You can specify a custom host and port if your SignalRGB instance is not running on the default location.

## Listing Effects

To get a list of all available effects:

```python
effects = client.get_effects()
for effect in effects:
    print(f"Effect: {effect.attributes.name}")
```

## Getting Effect Details

To get detailed information about a specific effect:

```python
effect = client.get_effect_by_name("Rain")
print(f"Effect Name: {effect.attributes.name}")
print(f"Description: {effect.attributes.description}")
print(f"Uses Audio: {effect.attributes.uses_audio}")
```

## Applying an Effect

To apply a specific effect:

```python
client.apply_effect_by_name("Rainbow Wave")
```

## Getting the Current Effect

To see which effect is currently active:

```python
current_effect = client.get_current_effect()
print(f"Current Effect: {current_effect.attributes.name}")
```

## Controlling Brightness

To get the current brightness level:

```python
brightness = client.brightness
print(f"Current brightness: {brightness}")
```

To set the brightness level (0-100):

```python
client.brightness = 75
print(f"Brightness set to: {client.brightness}")
```

## Enabling/Disabling the Canvas

To get the current enabled state:

```python
enabled = client.enabled
print(f"Canvas enabled: {enabled}")
```

To enable or disable the canvas:

```python
client.enabled = True
print(f"Canvas enabled: {client.enabled}")

client.enabled = False
print(f"Canvas disabled: {client.enabled}")
```

## Error Handling

The client provides custom exceptions for different types of errors. You can handle these exceptions to provide better error messages or implement retry logic:

```python
from signalrgb import SignalRGBClient, ConnectionError, APIError, EffectNotFoundError

client = SignalRGBClient()

try:
    client.apply_effect_by_name("Non-existent Effect")
except ConnectionError as e:
    print(f"Connection failed: {e}")
except EffectNotFoundError as e:
    print(f"Effect not found: {e}")
except APIError as e:
    print(f"API error occurred: {e}")
```

## Advanced Usage

### Refreshing Effects Cache

The client caches the list of effects for performance. If you need to refresh this cache:

```python
client.refresh_effects()
```

### Working with Effect Parameters

Some effects have parameters that can be adjusted. You can access these parameters like this:

```python
effect = client.get_effect_by_name("Falling Stars")
parameters = effect.attributes.parameters
print(f"Effect Parameters: {parameters}")
```

Note that the structure of parameters can vary between effects. Always check the specific effect's documentation or inspect the parameters dictionary to understand what options are available.

Remember to handle exceptions and implement proper error checking in your production code to ensure robustness and good user experience.

## Complete Example

Here's a more comprehensive example that demonstrates various features of the signalrgb-python library:

```python
from signalrgb import SignalRGBClient, ConnectionError, APIError, EffectNotFoundError

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

        # Control brightness
        client.brightness = 75
        print(f"\nBrightness set to: {client.brightness}")

        # Enable/disable the canvas
        client.enabled = True
        print(f"Canvas enabled: {client.enabled}")

        client.enabled = False
        print(f"Canvas disabled: {client.enabled}")

        # Refresh effects cache
        client.refresh_effects()
        print("\nEffects cache refreshed")

    except ConnectionError as e:
        print(f"Connection error: {e}")
    except EffectNotFoundError as e:
        print(f"Effect not found: {e}")
    except APIError as e:
        print(f"API error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
```

This example demonstrates how to use various features of the signalrgb-python library, including error handling, effect management, brightness control, and enabling/disabling the canvas.

## Best Practices

1. **Error Handling**: Always wrap your code in try-except blocks to handle potential errors gracefully.

2. **Resource Management**: If you're using the client in a long-running application, consider implementing a way to close the session when it's no longer needed.

3. **Caching**: The `get_effects()` method uses caching to improve performance. If you need the most up-to-date list of effects, use the `refresh_effects()` method before calling `get_effects()`.

4. **Rate Limiting**: Be mindful of how frequently you're making requests, especially in loops or automated scripts. Implement appropriate delays if necessary to avoid overwhelming the SignalRGB API.

5. **Logging**: Consider implementing logging in your application to track API interactions and any errors that occur.

By following these guidelines and exploring the various features of the signalrgb-python library, you can create robust and efficient applications that interact with SignalRGB Pro.