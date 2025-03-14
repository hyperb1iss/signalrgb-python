# SignalRGB Models API Reference

This page provides detailed API documentation for the data models used in the SignalRGB Python client. These models represent various data structures used in the SignalRGB API, including effects, responses, and error information.

## 🔍 Core Models

### Attributes

::: signalrgb.model.Attributes
    options:
      show_root_heading: true
      show_source: true

### Links

::: signalrgb.model.Links
    options:
      show_root_heading: true
      show_source: true

### Effect

::: signalrgb.model.Effect
    options:
      show_root_heading: true
      show_source: true

### EffectList

::: signalrgb.model.EffectList
    options:
      show_root_heading: true
      show_source: true

## 🛠️ State Models

### CurrentState

::: signalrgb.model.CurrentState
    options:
      show_root_heading: true
      show_source: true

### CurrentStateHolder

::: signalrgb.model.CurrentStateHolder
    options:
      show_root_heading: true
      show_source: true

## 📐 Layout Models

### Layout

::: signalrgb.model.Layout
    options:
      show_root_heading: true
      show_source: true

### LayoutList

::: signalrgb.model.LayoutList
    options:
      show_root_heading: true
      show_source: true

### CurrentLayoutHolder

::: signalrgb.model.CurrentLayoutHolder
    options:
      show_root_heading: true
      show_source: true

## 💾 Preset Models

### EffectPreset

::: signalrgb.model.EffectPreset
    options:
      show_root_heading: true
      show_source: true

### EffectPresetList

::: signalrgb.model.EffectPresetList
    options:
      show_root_heading: true
      show_source: true

## ⚠️ Error Models

### Error

::: signalrgb.model.Error
    options:
      show_root_heading: true
      show_source: true

## 🔄 Response Models

### SignalRGBResponse

::: signalrgb.model.SignalRGBResponse
    options:
      show_root_heading: true
      show_source: true

### EffectDetailsResponse

::: signalrgb.model.EffectDetailsResponse
    options:
      show_root_heading: true
      show_source: true

### EffectListResponse

::: signalrgb.model.EffectListResponse
    options:
      show_root_heading: true
      show_source: true

### CurrentStateResponse

::: signalrgb.model.CurrentStateResponse
    options:
      show_root_heading: true
      show_source: true

### LayoutListResponse

::: signalrgb.model.LayoutListResponse
    options:
      show_root_heading: true
      show_source: true

### CurrentLayoutResponse

::: signalrgb.model.CurrentLayoutResponse
    options:
      show_root_heading: true
      show_source: true

### EffectPresetListResponse

::: signalrgb.model.EffectPresetListResponse
    options:
      show_root_heading: true
      show_source: true

### EffectPresetResponse

::: signalrgb.model.EffectPresetResponse
    options:
      show_root_heading: true
      show_source: true

## 💡 Usage Example

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

# Extract parameters
parameters = effect.attributes.parameters
for param_name, param_data in parameters.items():
    print(f"Parameter: {param_name}")
    print(f"  Type: {param_data.get('type', 'Unknown')}")
    print(f"  Value: {param_data.get('value')}")

# Working with async client
import asyncio
from signalrgb import AsyncSignalRGBClient

async def get_effect_info():
    async with AsyncSignalRGBClient() as client:
        effect = await client.get_effect_by_name("Rainbow Wave")
        return effect.attributes.name, effect.id

# Run the async code
name, effect_id = asyncio.run(get_effect_info())
print(f"Got effect: {name} with ID: {effect_id}")
```

For more detailed usage examples, please refer to:
- [Python Library Usage](../usage/library.md) for the synchronous client
- [Asynchronous Library Usage](../async_usage.md) for the async client
