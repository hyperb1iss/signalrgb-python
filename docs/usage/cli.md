# Command-Line Interface

signalrgb-python ships with a Rich + Typer CLI for interacting with your SignalRGB instance. This
guide covers every command.

## 🎯 Basic syntax

```bash
signalrgb [OPTIONS] COMMAND [SUBCOMMAND] [ARGS]...
```

Get help at any level:

```bash
signalrgb --help
signalrgb effect --help
signalrgb canvas --help
```

## 📋 Commands

### 🎨 Effect commands

List all effects:

```bash
signalrgb effect list
```

Inspect a specific effect by name (or the current effect with no argument):

```bash
signalrgb effect "Psychedelic Dream"
signalrgb effect                         # show current effect
```

Apply an effect, optionally with a preset:

```bash
signalrgb effect apply "Rave Visualizer"
signalrgb effect apply "Rave Visualizer" --preset "Chill"
```

Search effects by name or description:

```bash
signalrgb effect search "ocean"
```

Navigate through history or apply a random effect:

```bash
signalrgb effect next_effect
signalrgb effect previous_effect
signalrgb effect random
```

Cycle through every effect with a configurable duration (seconds per effect):

```bash
signalrgb effect cycle --duration 10
```

Refresh the effects cache (force a re-fetch from the API):

```bash
signalrgb effect refresh
```

### 💾 Preset commands

List presets for the current effect:

```bash
signalrgb preset list
```

Apply a preset to the current effect:

```bash
signalrgb preset apply "My Fancy Preset"
```

### 📐 Layout commands

List all available layouts:

```bash
signalrgb layout list
```

Inspect or set the current layout:

```bash
signalrgb layout                    # show current layout
signalrgb layout set_layout "My Gaming Layout"
```

### 🎛️ Canvas commands

Show canvas state (enabled + brightness):

```bash
signalrgb canvas
```

Read or set brightness (0–100):

```bash
signalrgb canvas brightness           # read
signalrgb canvas brightness 75        # set
```

Enable, disable, or toggle the canvas:

```bash
signalrgb canvas enable
signalrgb canvas disable
signalrgb canvas toggle
```

## 🌐 Global options

Point at a remote SignalRGB instance:

```bash
signalrgb --host hyperia.home --port 16038 effect list
```

Enable the full-RGB gradient output mode:

```bash
signalrgb --full-rgb effect list
```

## 💡 Examples

Find an effect by keyword and pipe it:

```bash
signalrgb effect list | grep "Electric Space"
```

Dim and disable the canvas:

```bash
signalrgb canvas brightness 25
signalrgb canvas disable
```

Cycle through 5 random effects every 5 seconds:

```bash
for i in {1..5}; do
  signalrgb effect random
  sleep 5
done
```
