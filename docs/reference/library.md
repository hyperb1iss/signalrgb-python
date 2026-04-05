# Synchronous Client

`SignalRGBClient` provides a blocking interface to the SignalRGB API. Internally it wraps
`AsyncSignalRGBClient` behind a dedicated event loop.

## Constructor

```python
from signalrgb import SignalRGBClient

client = SignalRGBClient(
    host="localhost",  # API host
    port=16038,        # API port
    timeout=10.0,      # request timeout (seconds)
)
```

## Context manager

```python
with SignalRGBClient() as client:
    print(client.get_current_effect().attributes.name)
# resources cleaned up automatically
```

## Effects

| Method                       | Returns        | Description                    |
| ---------------------------- | -------------- | ------------------------------ |
| `get_effects()`              | `list[Effect]` | All available effects (cached) |
| `get_effect(id)`             | `Effect`       | Effect by ID                   |
| `get_effect_by_name(name)`   | `Effect`       | Effect by name                 |
| `get_current_effect()`       | `Effect`       | Currently active effect        |
| `apply_effect(id)`           | `None`         | Apply effect by ID             |
| `apply_effect_by_name(name)` | `None`         | Apply effect by name           |
| `apply_next_effect()`        | `Effect`       | Apply next in history          |
| `apply_previous_effect()`    | `Effect`       | Apply previous in history      |
| `apply_random_effect()`      | `Effect`       | Apply a random effect          |
| `refresh_effects()`          | `None`         | Clear the effects cache        |

## Presets

| Method                                      | Returns              | Description           |
| ------------------------------------------- | -------------------- | --------------------- |
| `get_effect_presets(effect_id)`             | `list[EffectPreset]` | Presets for an effect |
| `apply_effect_preset(effect_id, preset_id)` | `None`               | Apply a preset        |

## Layouts

| Method          | Returns        | Description           |
| --------------- | -------------- | --------------------- |
| `get_layouts()` | `list[Layout]` | All available layouts |

### Properties

| Property         | Type           | Description                   |
| ---------------- | -------------- | ----------------------------- |
| `current_layout` | `Layout` (r/w) | Get or set the current layout |

## Canvas

| Property         | Type                 | Description                      |
| ---------------- | -------------------- | -------------------------------- |
| `brightness`     | `int` (r/w)          | Canvas brightness (0–100)        |
| `enabled`        | `bool` (r/w)         | Canvas enabled state             |
| `current_effect` | `Effect` (read-only) | Alias for `get_current_effect()` |

## Exceptions

All exceptions inherit from `SignalRGBError`:

| Exception         | When                                |
| ----------------- | ----------------------------------- |
| `ConnectionError` | Can't reach the SignalRGB API       |
| `APIError`        | API returns a non-OK status         |
| `NotFoundError`   | Effect, preset, or layout not found |
