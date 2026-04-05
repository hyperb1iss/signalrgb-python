# Data Models Reference

This page documents the data models used by the SignalRGB Python client. They're [mashumaro](https://github.com/Fatal1ty/mashumaro) dataclasses that represent effects, responses, and error information exchanged with the SignalRGB API.

## 🎯 Core models

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

## 🔮 State models

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

## 📐 Layout models

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

## 💾 Preset models

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

## ⚠️ Error model

### Error

::: signalrgb.model.Error
    options:
      show_root_heading: true
      show_source: true

## 🔄 Response models

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

## 💡 Usage example

```python
from signalrgb import SignalRGBClient
from signalrgb.model import Effect

client = SignalRGBClient()

effect: Effect = client.get_effect_by_name("Sakura")
print(f"Name: {effect.attributes.name}")
print(f"Description: {effect.attributes.description}")
print(f"Uses audio: {effect.attributes.uses_audio}")

# Explore effect parameters
for name, param in effect.attributes.parameters.items():
    print(f"{name}: type={param.get('type', 'unknown')} value={param.get('value')}")
```

For more examples, see:

- [Python Library Usage](../usage/library.md) for the synchronous client
- [Async Library Usage](../async_usage.md) for the asynchronous client
