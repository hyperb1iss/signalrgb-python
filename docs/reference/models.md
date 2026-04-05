# Data Models

All models are [mashumaro](https://github.com/Fatal1ty/mashumaro) `@dataclass` classes with
`DataClassDictMixin` for JSON serialization.

## Effect

```python
@dataclass
class Effect(DataClassDictMixin):
    attributes: Attributes
    id: str
    links: Links
    type: str
```

### Attributes

```python
@dataclass
class Attributes(DataClassDictMixin):
    name: str
    description: str | None = None
    developer_effect: bool = False
    image: str | None = None
    parameters: dict[str, Any] = field(default_factory=dict)
    publisher: str | None = None
    uses_audio: bool = False
    uses_input: bool = False
    uses_meters: bool = False
    uses_video: bool = False
```

### Links

```python
@dataclass
class Links(DataClassDictMixin):
    apply: str | None = None
    self_link: str | None = None  # aliased from "self" in JSON
```

## Layout

```python
@dataclass
class Layout(DataClassDictMixin):
    id: str
    type: str
```

## EffectPreset

```python
@dataclass
class EffectPreset(DataClassDictMixin):
    id: str
    type: str
```

## CurrentState

Represents the current canvas state (the active effect, enabled flag, brightness):

```python
@dataclass
class CurrentState(DataClassDictMixin):
    name: str | None = None
    enabled: bool = False
    global_brightness: int = 0
```

## Error

Returned in API error responses:

```python
@dataclass
class Error(DataClassDictMixin):
    title: str
    code: str | None = None
    detail: str | None = None
```

## Response types

All API responses inherit from `SignalRGBResponse`:

```python
@dataclass
class SignalRGBResponse(DataClassDictMixin):
    api_version: str
    id: int
    method: str
    status: str
    params: dict[str, Any] = field(default_factory=dict)
    errors: list[Error] = field(default_factory=list)
```

Specialized response types:

| Class                      | `data` field type             |
| -------------------------- | ----------------------------- |
| `EffectDetailsResponse`    | `Effect \| None`              |
| `EffectListResponse`       | `EffectList \| None`          |
| `CurrentStateResponse`     | `CurrentStateHolder \| None`  |
| `LayoutListResponse`       | `dict[str, Any] \| None`      |
| `CurrentLayoutResponse`    | `CurrentLayoutHolder \| None` |
| `EffectPresetListResponse` | `EffectPresetList \| None`    |
| `EffectPresetResponse`     | `EffectPreset \| None`        |

## Working with parameters

Some effects expose tunable parameters via `effect.attributes.parameters`:

```python
effect = client.get_effect_by_name("Falling Stars")
for name, param in effect.attributes.parameters.items():
    print(f"{name}: {param.get('type', 'unknown')} = {param.get('value')}")
```

The shape varies per effect — inspect the dict to see what's available.
