#!/usr/bin/env python3
"""Example of using the AsyncSignalRGBClient class."""

import asyncio
import sys

from signalrgb import AsyncSignalRGBClient, Effect


async def list_effects(client: AsyncSignalRGBClient) -> list[Effect]:
    """List the first five available effects."""
    effects = await client.get_effects()
    print(f"\nFound {len(effects)} effects (showing first 5):")
    for i, effect in enumerate(effects[:5], 1):
        print(f"  {i}. {effect.attributes.name}")
    if len(effects) > 5:
        print(f"  ... and {len(effects) - 5} more")
    return effects


async def get_current_effect(client: AsyncSignalRGBClient) -> Effect:
    """Print and return the current effect."""
    effect = await client.get_current_effect()
    print(f"Current effect: {effect.attributes.name}")
    return effect


async def apply_random_effect(client: AsyncSignalRGBClient) -> None:
    """Apply a random effect."""
    effect = await client.apply_random_effect()
    print(f"Applied random effect: {effect.attributes.name}")


async def show_brightness(client: AsyncSignalRGBClient) -> int:
    """Print and return the current brightness level."""
    brightness = await client.get_brightness()
    print(f"Current brightness: {brightness}%")
    return brightness


async def toggle_enabled(client: AsyncSignalRGBClient) -> None:
    """Toggle the enabled state of the canvas."""
    enabled = await client.get_enabled()
    await client.set_enabled(not enabled)
    print(f"Canvas toggled: {'enabled' if not enabled else 'disabled'}")


async def main() -> None:
    """Run the demo against a running SignalRGB instance."""
    async with AsyncSignalRGBClient() as client:
        await get_current_effect(client)
        await show_brightness(client)
        await list_effects(client)

        answer = input("\nApply a random effect? (y/n): ")
        if answer.lower() == "y":
            await apply_random_effect(client)
            await get_current_effect(client)

        answer = input("\nToggle canvas enabled state? (y/n): ")
        if answer.lower() == "y":
            await toggle_enabled(client)
            await asyncio.sleep(1)
            await toggle_enabled(client)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
    except (ConnectionError, TimeoutError, asyncio.CancelledError) as e:
        print(f"Connection error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # noqa: BLE001
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
