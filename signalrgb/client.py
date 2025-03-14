"""
Synchronous client for interacting with the SignalRGB API.

This module provides a synchronous client class for interacting with the SignalRGB API,
allowing users to retrieve, apply, and manage lighting effects and layouts.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Iterator
from typing import Any, TypeVar

import requests

from .async_client import AsyncSignalRGBClient
from .constants import DEFAULT_HOST, DEFAULT_PORT, DEFAULT_TIMEOUT
from .model import (
    Effect,
    EffectPreset,
    Layout,
)

# Define a TypeVar for the return type
T = TypeVar('T')

class SignalRGBClient:
    """Client for interacting with the SignalRGB API.

    This class provides methods to interact with the SignalRGB API, allowing users
    to retrieve, apply, and manage lighting effects and layouts.

    This class is a wrapper around the AsyncSignalRGBClient that provides a synchronous
    interface to the API. Most methods simply delegate to the async client.
    """

    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, timeout: float = DEFAULT_TIMEOUT):
        """Initialize the SignalRGBClient.

        Args:
            host: The host of the SignalRGB API. Defaults to 'localhost'.
            port: The port of the SignalRGB API. Defaults to DEFAULT_PORT.
            timeout: The timeout for API requests in seconds. Defaults to 10.0.

        Example:
            >>> client = SignalRGBClient()
            >>> client = SignalRGBClient("192.168.1.100", 8080, 5.0)
        """
        self._base_url = f"http://{host}:{port}"
        self._timeout = timeout
        self._effects_cache: list[Effect] | None = None
        # For backward compatibility, we still maintain the session
        self._session = requests.Session()
        # Create an AsyncSignalRGBClient for internal use
        self._async_client = AsyncSignalRGBClient(host, port, timeout)
        # Create and manage an event loop for running async code
        self._loop = asyncio.new_event_loop()

    def __enter__(self) -> SignalRGBClient:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self._session.close()
        try:
            # Close the async client if the loop is still running
            if not self._loop.is_closed():
                self._loop.run_until_complete(self._async_client.aclose())
                self._loop.close()
        except RuntimeError:
            # The loop might already be closed, just ignore
            pass

    def _run_async(self, coro: Awaitable[T]) -> T:
        """Run an asynchronous coroutine in a synchronous context.

        Args:
            coro: The coroutine to run.

        Returns:
            The result of the coroutine with preserved type.
        """
        try:
            if self._loop.is_closed():
                self._loop = asyncio.new_event_loop()
            return self._loop.run_until_complete(coro)
        except RuntimeError as e:
            # If we get a runtime error about the event loop, create a new one
            if "This event loop is already running" in str(e):
                # Create a new event loop for this thread
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                self._loop = new_loop
                return self._loop.run_until_complete(coro)
            raise

    # Using a standard method with cached property pattern instead of lru_cache on method
    def _get_effects_cached(self) -> list[Effect]:
        """Internal method to get effects with caching."""
        return self._run_async(self._async_client.get_effects_cached())

    def get_effects(self) -> list[Effect]:
        """List available effects.

        Returns:
            List[Effect]: A list of available effects.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an error retrieving the effects.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> effects = client.get_effects()
            >>> print(f"Found {len(effects)} effects")
        """
        return self._run_async(self._async_client.get_effects())

    def get_effect(self, effect_id: str) -> Effect:
        """Get details of a specific effect.

        Args:
            effect_id (str): The ID of the effect to retrieve.

        Returns:
            Effect: The requested effect.

        Raises:
            NotFoundError: If the effect with the given ID is not found.
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> effect = client.get_effect("example_effect_id")
            >>> print(f"Effect name: {effect.attributes.name}")
        """
        return self._run_async(self._async_client.get_effect(effect_id))

    def get_effect_by_name(self, effect_name: str) -> Effect:
        """Get details of a specific effect by name.

        Args:
            effect_name: The name of the effect to retrieve.

        Returns:
            Effect: The requested effect.

        Raises:
            NotFoundError: If the effect with the given name is not found.
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> effect = client.get_effect_by_name("Rainbow Wave")
            >>> print(f"Effect ID: {effect.id}")
        """
        return self._run_async(self._async_client.get_effect_by_name(effect_name))

    @property
    def current_effect(self) -> Effect:
        """Get the current effect.

        Returns:
            Effect: The currently active effect.

        Raises:
            APIError: If there's an error retrieving the current effect.
        """
        return self.get_current_effect()

    def get_current_effect(self) -> Effect:
        """Get the current effect.

        Returns:
            Effect: The currently active effect.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> current_effect = client.get_current_effect()
            >>> print(f"Current effect: {current_effect.attributes.name}")
        """
        return self._run_async(self._async_client.get_current_effect())

    def _get_current_state(self) -> Any:  # Using Any for CurrentStateHolder
        """Get the current state of the SignalRGB instance.

        Returns:
            CurrentStateHolder: The current state of the SignalRGB instance.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.
        """
        return self._run_async(self._async_client.get_current_state())

    @property
    def brightness(self) -> int:
        """Get or set the current brightness level.

        Returns:
            int: The current brightness level (0-100).

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> print(f"Current brightness: {client.brightness}")
            >>> client.brightness = 75
            >>> print(f"New brightness: {client.brightness}")
        """
        return self._run_async(self._async_client.get_brightness())

    @brightness.setter
    def brightness(self, value: int) -> None:
        self._run_async(self._async_client.set_brightness(value))

    @property
    def enabled(self) -> bool:
        """Get or set the current enabled state of the canvas.

        Returns:
            bool: The current enabled state.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> print(f"Canvas enabled: {client.enabled}")
            >>> client.enabled = False
            >>> print(f"Canvas now disabled: {not client.enabled}")
        """
        return self._run_async(self._async_client.get_enabled())

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._run_async(self._async_client.set_enabled(value))

    def apply_effect(self, effect_id: str) -> None:
        """Apply an effect.

        Args:
            effect_id (str): The ID of the effect to apply.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> client.apply_effect("example_effect_id")
            >>> print("Effect applied successfully")
        """
        self._run_async(self._async_client.apply_effect(effect_id))

    def apply_effect_by_name(self, effect_name: str) -> None:
        """Apply an effect by name.

        Args:
            effect_name: The name of the effect to apply.

        Raises:
            NotFoundError: If the effect with the given name is not found.
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> client.apply_effect_by_name("Rainbow Wave")
            >>> print("Effect applied successfully")
        """
        self._run_async(self._async_client.apply_effect_by_name(effect_name))

    def get_effect_presets(self, effect_id: str) -> list[EffectPreset]:
        """Get presets for a specific effect.

        Args:
            effect_id (str): The ID of the effect to retrieve presets for.

        Returns:
            List[EffectPreset]: A list of effect presets.

        Raises:
            NotFoundError: If the effect with the given ID is not found.
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> presets = client.get_effect_presets("example_effect_id")
            >>> for preset in presets:
            ...     print(f"Preset ID: {preset.id}, Name: {preset.name}")
        """
        return self._run_async(self._async_client.get_effect_presets(effect_id))

    def apply_effect_preset(self, effect_id: str, preset_id: str) -> None:
        """Apply a preset for a specific effect.

        Args:
            effect_id (str): The ID of the effect to apply the preset to.
            preset_id (str): The ID of the preset to apply.

        Raises:
            NotFoundError: If the effect with the given ID is not found.
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> client.apply_effect_preset("example_effect_id", "My Fancy Preset 1")
            >>> print("Preset applied successfully")
        """
        self._run_async(self._async_client.apply_effect_preset(effect_id, preset_id))

    def get_next_effect(self) -> Effect | None:
        """Get information about the next effect in history.

        Returns:
            Optional[Effect]: The next effect if available, None otherwise.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> next_effect = client.get_next_effect()
            >>> if next_effect:
            ...     print(f"Next effect: {next_effect.attributes.name}")
            ... else:
            ...     print("No next effect available")
        """
        return self._run_async(self._async_client.get_next_effect())

    def apply_next_effect(self) -> Effect:
        """Apply the next effect in history or a random effect if there's no next effect.

        Returns:
            Effect: The newly applied effect.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> new_effect = client.apply_next_effect()
            >>> print(f"Applied effect: {new_effect.attributes.name}")
        """
        return self._run_async(self._async_client.apply_next_effect())

    def get_previous_effect(self) -> Effect | None:
        """Get information about the previous effect in history.

        Returns:
            Optional[Effect]: The previous effect if available, None otherwise.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> prev_effect = client.get_previous_effect()
            >>> if prev_effect:
            ...     print(f"Previous effect: {prev_effect.attributes.name}")
            ... else:
            ...     print("No previous effect available")
        """
        return self._run_async(self._async_client.get_previous_effect())

    def apply_previous_effect(self) -> Effect:
        """Apply the previous effect in history.

        Returns:
            Effect: The newly applied effect.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> new_effect = client.apply_previous_effect()
            >>> print(f"Applied effect: {new_effect.attributes.name}")
        """
        return self._run_async(self._async_client.apply_previous_effect())

    def apply_random_effect(self) -> Effect:
        """Apply a random effect.

        Returns:
            Effect: The newly applied random effect.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> random_effect = client.apply_random_effect()
            >>> print(f"Applied random effect: {random_effect.attributes.name}")
        """
        return self._run_async(self._async_client.apply_random_effect())

    @property
    def current_layout(self) -> Layout:
        """Get the current layout.

        Returns:
            Layout: The currently active layout.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> current_layout = client.current_layout
            >>> print(f"Current layout: {current_layout.id}")
        """
        return self._run_async(self._async_client.get_current_layout())

    @current_layout.setter
    def current_layout(self, layout_id: str) -> None:
        """Set the current layout.

        Args:
            layout_id: The ID of the layout to set as current.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> client.current_layout = "My Layout 1"
            >>> print(f"New current layout: {client.current_layout.id}")
        """
        self._run_async(self._async_client.set_current_layout(layout_id))

    def get_layouts(self) -> list[Layout]:
        """Get all available layouts.

        Returns:
            List[Layout]: A list of all available layouts.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> layouts = client.get_layouts()
            >>> for layout in layouts:
            ...     print(f"Layout: {layout.id}")
        """
        return self._run_async(self._async_client.get_layouts())

    def refresh_effects(self) -> None:
        """Refresh the cached effects.

        This method clears the cache for the get_effects method, forcing a fresh
        retrieval of effects on the next call.

        Example:
            >>> client = SignalRGBClient()
            >>> client.refresh_effects()
            >>> fresh_effects = client.get_effects()
        """
        self._run_async(self._async_client.refresh_effects())

    def __repr__(self) -> str:
        return f"SignalRGBClient(base_url='{self._base_url}')"


class EffectIterator:
    """Iterator for effects in SignalRGB."""

    def __init__(self, client: SignalRGBClient):
        self._client = client
        self._effects = iter(client.get_effects())

    def __iter__(self) -> Iterator[Effect]:
        return self

    def __next__(self) -> Effect:
        return next(self._effects)
