# Command-Line Interface (CLI) Usage

signalrgb-python provides a user-friendly command-line interface for interacting with your SignalRGB setup. This guide covers the basic usage of the CLI.

## Basic Syntax

The basic syntax for using the SignalRGB CLI is:

```bash
signalrgb [OPTIONS] COMMAND [SUBCOMMAND] [ARGS]...
```

You can always use the `--help` option to get more information about available commands and options:

```bash
signalrgb --help
```

## Available Commands

### Effect Commands

#### List Effects

To list all available lighting effects:

```bash
signalrgb effect list
```

#### Get Effect Details

To get detailed information about a specific effect:

```bash
signalrgb effect "Effect Name"
```

Replace "Effect Name" with the name of the effect you want to inspect.

#### Apply an Effect

To apply a specific effect:

```bash
signalrgb effect apply "Effect Name"
```

#### Get Current Effect

To see which effect is currently active:

```bash
signalrgb effect
```

### Preset Commands

#### List Presets

To list presets for the current effect:

```bash
signalrgb preset list
```

#### Apply a Preset

To apply a preset to the current effect:

```bash
signalrgb preset apply "Preset Name"
```

### Layout Commands

#### List Layouts

To list all available layouts:

```bash
signalrgb layout list
```

#### Set Current Layout

To set the current layout:

```bash
signalrgb layout set "Layout Name"
```

### Canvas Commands

#### Control Brightness

To set the brightness level (0-100):

```bash
signalrgb canvas brightness 75
```

To get the current brightness level:

```bash
signalrgb canvas brightness
```

#### Enable/Disable Canvas

To enable the canvas:

```bash
signalrgb canvas enable
```

To disable the canvas:

```bash
signalrgb canvas disable
```

## Global Options

You can specify a custom host and port for all commands:

```bash
signalrgb --host my-pc.local --port 16038 effect list
```

## Examples

Here are some example use cases:

1. List all effects and pipe the output to `grep` to find a specific effect:

   ```bash
   signalrgb effect list | grep "Electric Space"
   ```

2. Apply the "Rave Visualizer" effect:

   ```bash
   signalrgb effect apply "Rave Visualizer"
   ```

3. Get details of the current effect and save it to a file:

   ```bash
   signalrgb effect > current_effect.txt
   ```

4. Set the brightness to 50%:

   ```bash
   signalrgb canvas brightness 50
   ```

5. Enable the canvas:

   ```bash
   signalrgb canvas enable
   ```

6. List and apply a preset:

   ```bash
   signalrgb preset list
   signalrgb preset apply "Cool Preset"
   ```

7. Switch to a different layout:

   ```bash
   signalrgb layout set "Gaming Setup"
   ```

Remember to refer to the `--help` option for each command to see all available options and arguments.
