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
