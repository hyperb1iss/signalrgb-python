# Introduction

signalrgb-python is a Python client library and CLI for controlling
[SignalRGB Pro](https://signalrgb.com) lighting effects, presets, layouts, and canvas state.

## What you get

- **`SignalRGBClient`** — synchronous client for scripts and tools
- **`AsyncSignalRGBClient`** — native httpx async client for asyncio apps and Home Assistant
- **`signalrgb` CLI** — Rich + Typer command-line interface with subcommands for effects, presets,
  layouts, and canvas

## How it works

The library talks to the [SignalRGB REST API](https://docs.signalrgb.com/signalrgb-api)
(localhost:16038 by default). The async client is the primary implementation; the sync client wraps
it behind a blocking event loop.

## Prerequisites

- **Python 3.13+**
- **[SignalRGB Pro](https://www.signalrgb.com/pro/)** — the REST API requires a Pro license

## Next steps

- [Installation](./installation) — install the library
- [Quick Start](./quick-start) — get up and running in 60 seconds
