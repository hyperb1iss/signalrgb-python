# SignalRGB Models API Reference

This page provides detailed API documentation for the data models used in the SignalRGB Python client. These models represent various data structures used in the SignalRGB API, including effects, responses, and error information.

## Attributes

::: signalrgb.model.Attributes
    options:
      show_root_heading: true
      show_source: true

## Links

::: signalrgb.model.Links
    options:
      show_root_heading: true
      show_source: true

## Effect

::: signalrgb.model.Effect
    options:
      show_root_heading: true
      show_source: true

## EffectList

::: signalrgb.model.EffectList
    options:
      show_root_heading: true
      show_source: true

## Error

::: signalrgb.model.Error
    options:
      show_root_heading: true
      show_source: true

## SignalRGBResponse

::: signalrgb.model.SignalRGBResponse
    options:
      show_root_heading: true
      show_source: true

## EffectDetailsResponse

::: signalrgb.model.EffectDetailsResponse
    options:
      show_root_heading: true
      show_source: true

## EffectListResponse

::: signalrgb.model.EffectListResponse
    options:
      show_root_heading: true
      show_source: true

## Usage Example

Here's a basic example of how to work with these models:

```python
from signalrgb import SignalRGBClient
from signalrgb.model import Effect, Attributes

# Initialize the client
client = SignalRGBClient()

# Get an effect
effect: Effect = client.get_effect_by_name("Sakura")

# Access effect attributes
print(f"Effect name: {effect.attributes.name}")
print(f"Effect description: {effect.attributes.description}")
print(f"Effect uses audio: {effect.attributes.uses_audio}")

# Create a new effect (note: this is just an example, you can't actually create new effects via the API)
new_effect = Effect(
    id="custom_effect_1",
    type="lighting",
    links=Links(apply="/api/v1/effects/custom_effect_1/apply"),
    attributes=Attributes(
        name="My Custom Effect",
        description="A custom lighting effect",
        uses_audio=True
    )
)
```

For more detailed usage examples, please refer to the [Python Library Usage](../usage/library.md) guide.
