# Command-Line Interface (CLI) Usage

signalrgb-python provides a user-friendly command-line interface for interacting with your SignalRGB setup. This guide covers the basic usage of the CLI.

## Basic Syntax

The basic syntax for using the SignalRGB CLI is:

```bash
signalrgb [OPTIONS] COMMAND [ARGS]...
```

You can always use the `--help` option to get more information about available commands and options:

```bash
signalrgb --help
```

## Available Commands

### List Effects

To list all available lighting effects:

```bash
signalrgb list-effects
```

### Get Effect Details

To get detailed information about a specific effect:

```bash
signalrgb get-effect "Effect Name"
```

Replace "Effect Name" with the name of the effect you want to inspect.

### Apply an Effect

To apply a specific effect:

```bash
signalrgb apply-effect "Effect Name"
```

### Get Current Effect

To see which effect is currently active:

```bash
signalrgb current-effect
```

## Global Options

You can specify a custom host and port for all commands:

```bash
signalrgb --host my-pc.local --port 16038 list-effects
```

## Examples

Here are some example use cases:

1. List all effects and pipe the output to `grep` to find a specific effect:

   ```bash
   signalrgb list-effects | grep "Electric Space"
   ```

2. Apply the "Rave Visualizer" effect:

   ```bash
   signalrgb apply-effect "Rave Visualizer"
   ```

3. Get details of the current effect and save it to a file:

   ```bash
   signalrgb current-effect > current_effect.txt
   ```

Remember to refer to the `--help` option for each command to see all available options and arguments.
