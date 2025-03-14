# pylint: disable=too-many-public-methods

"""
Async client for interacting with the SignalRGB API.

This module provides an asynchronous client class for interacting with the SignalRGB API,
allowing users to retrieve, apply, and manage lighting effects and layouts.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import os
from typing import Any

import httpx

from .constants import DEBUG_ENV_VAR, DEFAULT_HOST, DEFAULT_PORT, DEFAULT_TIMEOUT, LIGHTING_V1, SCENES_V1
from .exceptions import APIError, ConnectionError, NotFoundError, SignalRGBError
from .model import (
    CurrentLayoutResponse,
    CurrentStateHolder,
    CurrentStateResponse,
    Effect,
    EffectDetailsResponse,
    EffectListResponse,
    EffectPreset,
    EffectPresetListResponse,
    EffectPresetResponse,
    Error,
    Layout,
    LayoutListResponse,
    SignalRGBResponse,
)


class AsyncSignalRGBClient:
    """Async client for interacting with the SignalRGB API.

    This class provides asynchronous methods to interact with the SignalRGB API, allowing users
    to retrieve, apply, and manage lighting effects and layouts.
    """

    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, timeout: float = DEFAULT_TIMEOUT):
        """Initialize the AsyncSignalRGBClient.

        Args:
            host: The host of the SignalRGB API. Defaults to 'localhost'.
            port: The port of the SignalRGB API. Defaults to DEFAULT_PORT.
            timeout: The timeout for API requests in seconds. Defaults to 10.0.

        Example:
            >>> client = AsyncSignalRGBClient()
            >>> client = AsyncSignalRGBClient("192.168.1.100", 8080, 5.0)
        """
        self._base_url = f"http://{host}:{port}"
        self._timeout = timeout
        self._effects_cache: list[Effect] | None = None
        self._client = httpx.AsyncClient(timeout=timeout)

    async def __aenter__(self) -> AsyncSignalRGBClient:
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self._client.aclose()

    @asynccontextmanager
    async def _request_context(self, method: str, endpoint: str, **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        """Async context manager for making API requests.

        This method handles common exception cases and debug logging.

        Args:
            method: The HTTP method to use for the request.
            endpoint: The API endpoint to request.
            **kwargs: Additional arguments to pass to the request.

        Yields:
            The JSON response from the API.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.
        """
        url = f"{self._base_url}{endpoint}"
        debug = os.getenv(DEBUG_ENV_VAR, "0") == "1"

        if debug:
            pass

        try:
            response = await self._client.request(method, url, **kwargs)
            response.raise_for_status()

            if debug:
                pass

            yield response.json()
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to SignalRGB API: {e}", Error(title=str(e))) from e
        except httpx.TimeoutException as e:
            raise ConnectionError("Request timed out", Error(title="Request Timeout")) from e
        except httpx.HTTPStatusError as e:
            # Create error object based on response
            error: Error
            if e.response is not None and hasattr(e.response, "json"):
                try:
                    json_data = e.response.json()
                    if "errors" in json_data and json_data["errors"] and isinstance(json_data["errors"], list):
                        error = Error.from_dict(json_data["errors"][0])
                    else:
                        error = Error(title=str(e))
                except Exception: # noqa: BLE001
                    error = Error(title=str(e))
            else:
                error = Error(title=str(e))
            raise APIError(f"HTTP error occurred: {e}", error) from e
        except httpx.RequestError as e:
            error = Error(title=str(e))
            raise APIError(f"An error occurred while making the request: {e}", error) from e
        except (ValueError, TypeError) as e:
            # More specific exceptions instead of catching generic Exception
            raise SignalRGBError(f"An unexpected error occurred: {e}") from e

    async def _get_effects_cached(self) -> list[Effect]:
        """Internal method to get effects with caching."""
        if self._effects_cache is None:
            async with self._request_context("GET", f"{LIGHTING_V1}/effects") as data:
                response = EffectListResponse.from_dict(data)
                self._ensure_response_ok(response)
                effects = response.data
                if effects is None or effects.items is None:
                    raise APIError("No effects data in the response")
                self._effects_cache = effects.items
        return self._effects_cache

    async def get_effects(self) -> list[Effect]:
        """List available effects asynchronously.

        Returns:
            List[Effect]: A list of available effects.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an error retrieving the effects.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> async with AsyncSignalRGBClient() as client:
            >>>     effects = await client.get_effects()
            >>>     print(f"Found {len(effects)} effects")
        """
        return await self._get_effects_cached()

    async def get_effect(self, effect_id: str) -> Effect:
        """Get details of a specific effect asynchronously.

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
            >>> async with AsyncSignalRGBClient() as client:
            >>>     effect = await client.get_effect("example_effect_id")
            >>>     print(f"Effect name: {effect.attributes.name}")
        """
        try:
            async with self._request_context("GET", f"{LIGHTING_V1}/effects/{effect_id}") as data:
                response = EffectDetailsResponse.from_dict(data)
                self._ensure_response_ok(response)
                if response.data is None:
                    raise APIError("No effect data in the response")
                return response.data
        except APIError as e:
            if e.error and e.error.code == "not_found":
                raise NotFoundError(f"Effect with ID '{effect_id}' not found", e.error) from e
            raise

    async def get_effect_by_name(self, effect_name: str) -> Effect:
        """Get details of a specific effect by name asynchronously.

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
            >>> async with AsyncSignalRGBClient() as client:
            >>>     effect = await client.get_effect_by_name("Rainbow Wave")
            >>>     print(f"Effect ID: {effect.id}")
        """
        effects = await self.get_effects()
        effect = next((e for e in effects if e.attributes.name == effect_name), None)
        if effect is None:
            raise NotFoundError(f"Effect '{effect_name}' not found")
        return await self.get_effect(effect.id)

    async def get_current_effect(self) -> Effect:
        """Get the current effect asynchronously.

        Returns:
            Effect: The currently active effect.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> async with AsyncSignalRGBClient() as client:
            >>>     current_effect = await client.get_current_effect()
            >>>     print(f"Current effect: {current_effect.attributes.name}")
        """
        state = await self._get_current_state()
        if state.attributes is None:
            raise APIError("No current effect data in the response")
        return await self.get_effect(state.id)

    async def _get_current_state(self) -> CurrentStateHolder:
        """Get the current state of the SignalRGB instance asynchronously.

        Returns:
            CurrentStateHolder: The current state of the SignalRGB instance.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.
        """
        async with self._request_context("GET", LIGHTING_V1) as data:
            response = CurrentStateResponse.from_dict(data)
            self._ensure_response_ok(response)
            if response.data is None:
                raise APIError("No current state data in the response")
            return response.data

    async def get_brightness(self) -> int:
        """Get the current brightness level asynchronously.

        Returns:
            int: The current brightness level (0-100).

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> async with AsyncSignalRGBClient() as client:
            >>>     brightness = await client.get_brightness()
            >>>     print(f"Current brightness: {brightness}")
        """
        state = await self._get_current_state()
        return state.attributes.global_brightness

    async def set_brightness(self, value: int) -> None:
        """Set the brightness level asynchronously.

        Args:
            value: The brightness level to set (0-100).

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> async with AsyncSignalRGBClient() as client:
            >>>     await client.set_brightness(75)
            >>>     print("Brightness set to 75%")
        """
        async with self._request_context(
            "PATCH",
            f"{LIGHTING_V1}/global_brightness",
            json={"global_brightness": value},
        ):
            pass

    async def get_enabled(self) -> bool:
        """Get the current enabled state of the canvas asynchronously.

        Returns:
            bool: The current enabled state.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> async with AsyncSignalRGBClient() as client:
            >>>     enabled = await client.get_enabled()
            >>>     print(f"Canvas enabled: {enabled}")
        """
        state = await self._get_current_state()
        return state.attributes.enabled

    async def set_enabled(self, value: bool) -> None:
        """Set the enabled state of the canvas asynchronously.

        Args:
            value: Whether to enable the canvas.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> async with AsyncSignalRGBClient() as client:
            >>>     await client.set_enabled(False)
            >>>     print("Canvas disabled")
        """
        async with self._request_context("PATCH", f"{LIGHTING_V1}/enabled", json={"enabled": value}):
            pass

    async def apply_effect(self, effect_id: str) -> None:
        """Apply an effect asynchronously.

        Args:
            effect_id (str): The ID of the effect to apply.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> async with AsyncSignalRGBClient() as client:
            >>>     await client.apply_effect("example_effect_id")
            >>>     print("Effect applied successfully")
        """
        async with self._request_context("POST", f"{LIGHTING_V1}/effects/{effect_id}/apply") as data:
            response = SignalRGBResponse.from_dict(data)
            self._ensure_response_ok(response)

    async def apply_effect_by_name(self, effect_name: str) -> None:
        """Apply an effect by name asynchronously.

        Args:
            effect_name: The name of the effect to apply.

        Raises:
            NotFoundError: If the effect with the given name is not found.
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> async with AsyncSignalRGBClient() as client:
            >>>     await client.apply_effect_by_name("Rainbow Wave")
            >>>     print("Effect applied successfully")
        """
        effect = await self.get_effect_by_name(effect_name)
        apply_url = effect.links.apply
        if apply_url is None:
            # Fallback if apply link is missing
            await self.apply_effect(effect.id)
        else:
            async with self._request_context("POST", apply_url):
                pass

    async def get_effect_presets(self, effect_id: str) -> list[EffectPreset]:
        """Get presets for a specific effect asynchronously.

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
            >>> async with AsyncSignalRGBClient() as client:
            >>>     presets = await client.get_effect_presets("example_effect_id")
            >>>     for preset in presets:
            >>>         print(f"Preset ID: {preset.id}")
        """
        try:
            async with self._request_context("GET", f"{LIGHTING_V1}/effects/{effect_id}/presets") as data:
                response = EffectPresetListResponse.from_dict(data)
                self._ensure_response_ok(response)
                if response.data is None:
                    raise APIError("No preset data in the response")
                return response.data.items
        except APIError as e:
            if e.error and e.error.code == "not_found":
                raise NotFoundError(f"Effect with ID '{effect_id}' not found", e.error) from e
            raise

    async def apply_effect_preset(self, effect_id: str, preset_id: str) -> None:
        """Apply a preset for a specific effect asynchronously.

        Args:
            effect_id (str): The ID of the effect to apply the preset to.
            preset_id (str): The ID of the preset to apply.

        Raises:
            NotFoundError: If the effect with the given ID is not found.
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> async with AsyncSignalRGBClient() as client:
            >>>     await client.apply_effect_preset("example_effect_id", "My Fancy Preset 1")
            >>>     print("Preset applied successfully")
        """
        try:
            async with self._request_context(
                "PATCH",
                f"{LIGHTING_V1}/effects/{effect_id}/presets",
                json={"preset": preset_id},
            ) as data:
                response = EffectPresetResponse.from_dict(data)
                self._ensure_response_ok(response)
        except APIError as e:
            if e.error and e.error.code == "not_found":
                raise NotFoundError(
                    f"Effect with ID '{effect_id}' or preset '{preset_id}' not found",
                    e.error,
                ) from e
            raise

    async def get_next_effect(self) -> Effect | None:
        """Get information about the next effect in history asynchronously.

        Returns:
            Optional[Effect]: The next effect if available, None otherwise.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> async with AsyncSignalRGBClient() as client:
            >>>     next_effect = await client.get_next_effect()
            >>>     if next_effect:
            >>>         print(f"Next effect: {next_effect.attributes.name}")
            >>>     else:
            >>>         print("No next effect available")
        """
        try:
            async with self._request_context("GET", f"{LIGHTING_V1}/next") as data:
                response = EffectDetailsResponse.from_dict(data)
                self._ensure_response_ok(response)
                return response.data
        except APIError as e:
            if e.error and e.error.code == "409":
                return None
            raise

    async def apply_next_effect(self) -> Effect:
        """Apply the next effect in history or a random effect if there's no next effect asynchronously.

        Returns:
            Effect: The newly applied effect.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> async with AsyncSignalRGBClient() as client:
            >>>     new_effect = await client.apply_next_effect()
            >>>     print(f"Applied effect: {new_effect.attributes.name}")
        """
        async with self._request_context("POST", f"{LIGHTING_V1}/next") as data:
            response = EffectDetailsResponse.from_dict(data)
            self._ensure_response_ok(response)
            if response.data is None:
                raise APIError("No effect data in the response")
            return response.data

    async def get_previous_effect(self) -> Effect | None:
        """Get information about the previous effect in history asynchronously.

        Returns:
            Optional[Effect]: The previous effect if available, None otherwise.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> async with AsyncSignalRGBClient() as client:
            >>>     prev_effect = await client.get_previous_effect()
            >>>     if prev_effect:
            >>>         print(f"Previous effect: {prev_effect.attributes.name}")
            >>>     else:
            >>>         print("No previous effect available")
        """
        try:
            async with self._request_context("GET", f"{LIGHTING_V1}/previous") as data:
                response = EffectDetailsResponse.from_dict(data)
                self._ensure_response_ok(response)
                return response.data
        except APIError as e:
            if e.error and e.error.code == "409":
                return None
            raise

    async def apply_previous_effect(self) -> Effect:
        """Apply the previous effect in history asynchronously.

        Returns:
            Effect: The newly applied effect.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> async with AsyncSignalRGBClient() as client:
            >>>     new_effect = await client.apply_previous_effect()
            >>>     print(f"Applied effect: {new_effect.attributes.name}")
        """
        async with self._request_context("POST", f"{LIGHTING_V1}/previous") as data:
            response = EffectDetailsResponse.from_dict(data)
            self._ensure_response_ok(response)
            if response.data is None:
                raise APIError("No effect data in the response")
            return response.data

    async def apply_random_effect(self) -> Effect:
        """Apply a random effect asynchronously.

        Returns:
            Effect: The newly applied random effect.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> async with AsyncSignalRGBClient() as client:
            >>>     random_effect = await client.apply_random_effect()
            >>>     print(f"Applied random effect: {random_effect.attributes.name}")
        """
        async with self._request_context("POST", f"{LIGHTING_V1}/shuffle") as data:
            response = EffectDetailsResponse.from_dict(data)
            self._ensure_response_ok(response)
            if response.data is None:
                raise APIError("No effect data in the response")
            return response.data

    async def get_current_layout(self) -> Layout:
        """Get the current layout asynchronously.

        Returns:
            Layout: The currently active layout.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> async with AsyncSignalRGBClient() as client:
            >>>     current_layout = await client.get_current_layout()
            >>>     print(f"Current layout: {current_layout.id}")
        """
        async with self._request_context("GET", f"{SCENES_V1}/current_layout") as data:
            response = CurrentLayoutResponse.from_dict(data)
            self._ensure_response_ok(response)
            if response.data is None or response.data.current_layout is None:
                raise APIError("No current layout data in the response")
            return response.data.current_layout

    async def set_current_layout(self, layout_id: str) -> None:
        """Set the current layout asynchronously.

        Args:
            layout_id: The ID of the layout to set as current.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> async with AsyncSignalRGBClient() as client:
            >>>     await client.set_current_layout("My Layout 1")
            >>>     current = await client.get_current_layout()
            >>>     print(f"New current layout: {current.id}")
        """
        async with self._request_context("PATCH", f"{SCENES_V1}/current_layout", json={"layout": layout_id}) as data:
            response = CurrentLayoutResponse.from_dict(data)
            self._ensure_response_ok(response)
            if response.data is None or response.data.current_layout is None:
                raise APIError("No current layout data in the response")
            if response.data.current_layout.id != layout_id:
                raise APIError(f"Failed to set layout to '{layout_id}'")

    async def get_layouts(self) -> list[Layout]:
        """Get all available layouts asynchronously.

        Returns:
            List[Layout]: A list of all available layouts.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.

        Example:
            >>> async with AsyncSignalRGBClient() as client:
            >>>     layouts = await client.get_layouts()
            >>>     for layout in layouts:
            >>>         print(f"Layout: {layout.id}")
        """
        async with self._request_context("GET", f"{SCENES_V1}/layouts") as data:
            response = LayoutListResponse.from_dict(data)
            self._ensure_response_ok(response)
            if "data" not in data or "items" not in data["data"]:
                raise APIError("No layouts data in the response")
            return [Layout.from_dict(item) for item in data["data"]["items"]]

    def _ensure_response_ok(self, response: SignalRGBResponse) -> None:
        """Ensure the response status is 'ok'.

        Args:
            response: The response to check.

        Raises:
            APIError: If the response status is not 'ok'.
        """
        if response.status != "ok":
            error = response.errors[0] if response.errors else None
            raise APIError(f"API returned non-OK status: {response.status}", error)

    async def refresh_effects(self) -> None:
        """Refresh the cached effects asynchronously.

        This method clears the cache for the get_effects method, forcing a fresh
        retrieval of effects on the next call.

        Example:
            >>> async with AsyncSignalRGBClient() as client:
            >>>     await client.refresh_effects()
            >>>     fresh_effects = await client.get_effects()
        """
        self._effects_cache = None

    def __repr__(self) -> str:
        return f"AsyncSignalRGBClient(base_url='{self._base_url}')"

    async def aclose(self) -> None:
        """Close the async client explicitly.

        This method ensures resources are properly released when the client is no longer needed.
        """
        await self._client.aclose()

    async def get_effects_cached(self) -> list[Effect]:
        """Get effects with caching.

        Returns cached effects if available, otherwise retrieves them from the API.

        Returns:
            List[Effect]: A list of available effects.
        """
        return await self._get_effects_cached()

    async def get_current_state(self) -> CurrentStateHolder:
        """Get the current state of the SignalRGB instance.

        Returns:
            CurrentStateHolder: The current state of the SignalRGB instance.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBError: For any other unexpected errors.
        """
        return await self._get_current_state()
