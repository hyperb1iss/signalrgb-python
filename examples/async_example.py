#!/usr/bin/env python3
"""Example of using the AsyncSignalRGBClient class."""

import asyncio
import sys

from signalrgb import AsyncSignalRGBClient, Effect


async def list_effects(client: AsyncSignalRGBClient) -> list[Effect]:
    """List all available effects."""
    effects = await client.get_effects()
    for _i, _effect in enumerate(effects[:5], 1):
        pass

    if len(effects) > 5:
        pass

    return effects


async def get_current_effect(client: AsyncSignalRGBClient) -> Effect:
    """Get the current effect."""
    return await client.get_current_effect()


async def apply_random_effect(client: AsyncSignalRGBClient) -> None:
    """Apply a random effect."""
    await client.apply_random_effect()


async def show_brightness(client: AsyncSignalRGBClient) -> int:
    """Show the current brightness level."""
    return await client.get_brightness()


async def toggle_enabled(client: AsyncSignalRGBClient) -> None:
    """Toggle the enabled state of the canvas."""
    enabled = await client.get_enabled()

    await client.set_enabled(not enabled)


async def main() -> None:
    """Main function."""
    # Create the client
    async with AsyncSignalRGBClient() as client:
        # Show the current effect
        await get_current_effect(client)

        # Show the current brightness
        await show_brightness(client)

        # List available effects (limited to first 5)
        await list_effects(client)

        # Ask if user wants to apply a random effect
        answer = input("\nApply a random effect? (y/n): ")
        if answer.lower() == "y":
            await apply_random_effect(client)
            # Show the new current effect
            await get_current_effect(client)

        # Ask if user wants to toggle the canvas
        answer = input("\nToggle canvas enabled state? (y/n): ")
        if answer.lower() == "y":
            await toggle_enabled(client)
            # Wait a second
            await asyncio.sleep(1)
            # Toggle it back
            await toggle_enabled(client)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
    except (ConnectionError, TimeoutError, asyncio.CancelledError):
        sys.exit(1)
    except Exception:  # noqa: BLE001
        sys.exit(1)
