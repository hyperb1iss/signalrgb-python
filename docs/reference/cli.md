# CLI Reference

The `signalrgb` CLI is built with Typer + Rich. All commands are organized under subcommand groups.

## Global options

```bash
signalrgb --host <host> --port <port> [--full-rgb] COMMAND
```

| Option       | Default     | Description                         |
| ------------ | ----------- | ----------------------------------- |
| `--host`     | `localhost` | SignalRGB API host                  |
| `--port`     | `16038`     | SignalRGB API port                  |
| `--full-rgb` | off         | Enable rainbow gradient output mode |

## `effect` — Manage effects

```bash
signalrgb effect                          # show current effect
signalrgb effect "Effect Name"            # show specific effect by name
signalrgb effect list                     # list all effects
signalrgb effect apply "Effect Name"      # apply an effect
signalrgb effect search "query"           # search by name or description
signalrgb effect random                   # apply a random effect
signalrgb effect next_effect              # next in history
signalrgb effect previous_effect          # previous in history
signalrgb effect cycle [--duration N]     # cycle through all (default 5s each)
signalrgb effect refresh                  # clear the effects cache
```

## `preset` — Manage presets

```bash
signalrgb preset                          # show current preset info
signalrgb preset list                     # list presets for current effect
signalrgb preset apply "Preset Name"      # apply preset to current effect
```

## `layout` — Manage layouts

```bash
signalrgb layout                          # show current layout
signalrgb layout list                     # list all layouts
signalrgb layout set_layout "Name"        # set current layout
```

## `canvas` — Canvas control

```bash
signalrgb canvas                          # show state + brightness
signalrgb canvas brightness               # read current brightness
signalrgb canvas brightness 75            # set brightness (0–100)
signalrgb canvas enable                   # enable the canvas
signalrgb canvas disable                  # disable the canvas
signalrgb canvas toggle                   # toggle enabled state
```
