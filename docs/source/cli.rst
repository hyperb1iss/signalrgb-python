Command-Line Interface Reference
================================

The SignalRGB Python Client provides a command-line interface for interacting with SignalRGB. Here's a detailed reference of all available commands and options.

Global Options
--------------

These options can be used with any command:

--host TEXT  The host where SignalRGB is running. Default is 'localhost'.
--port INTEGER  The port SignalRGB is listening on. Default is 16038.
--help  Show this message and exit.

Commands
--------

list-effects
~~~~~~~~~~~~

List all available effects.

Usage:
    signalrgb list-effects

get-effect
~~~~~~~~~~

Get details of a specific effect.

Usage:
    signalrgb get-effect EFFECT_NAME

Arguments:
    EFFECT_NAME  The name of the effect to get details for.

apply-effect
~~~~~~~~~~~~

Apply an effect.

Usage:
    signalrgb apply-effect EFFECT_NAME

Arguments:
    EFFECT_NAME  The name of the effect to apply.

current-effect
~~~~~~~~~~~~~~

Get the current effect.

Usage:
    signalrgb current-effect

Examples
--------

List all effects:
    signalrgb list-effects

Get details of the "Rainbow Wave" effect:
    signalrgb get-effect "Rainbow Wave"

Apply the "Audio Visualizer" effect:
    signalrgb apply-effect "Audio Visualizer"

Get the current effect:
    signalrgb current-effect

Use a custom host and port:
    signalrgb --host 192.168.1.100 --port 16038 list-effects
