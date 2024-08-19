"""
Client for interacting with the SignalRGB API.

This module provides a client class for interacting with the SignalRGB API,
allowing users to retrieve, apply, and manage lighting effects and layouts.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from functools import lru_cache
from typing import Any, Dict, Iterator, List, Optional

import requests
from requests.exceptions import RequestException, Timeout

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

DEFAULT_PORT = 16038
LIGHTING_V1 = "/api/v1/lighting"
SCENES_V1 = "/api/v1/scenes"


class SignalRGBException(Exception):
    """Base exception for SignalRGB errors.

    This exception is raised when a general error occurs during API interactions.

    Attributes:
        message (str): The error message.
        error (Optional[Error]): The Error object containing additional error details.
    """

    def __init__(self, message: str, error: Optional[Error] = None):
        super().__init__(message)
        self.error = error

    @property
    def code(self) -> Optional[str]:
        """Optional[str]: The error code, if available."""
        return self.error.code if self.error else None

    @property
    def title(self) -> Optional[str]:
        """Optional[str]: The error title, if available."""
        return self.error.title if self.error else None

    @property
    def detail(self) -> Optional[str]:
        """Optional[str]: The detailed error message, if available."""
        return self.error.detail if self.error else None


class ConnectionError(SignalRGBException):
    """Exception raised for connection errors.

    This exception is raised when there's an issue connecting to the SignalRGB API.
    """


class APIError(SignalRGBException):
    """Exception raised for API errors.

    This exception is raised when the API returns an error response.
    """


class NotFoundError(SignalRGBException):
    """Exception raised when an item is not found.

    This exception is raised when trying to retrieve or apply a non-existent effect, preset, or layout.
    """


class SignalRGBClient:
    """Client for interacting with the SignalRGB API.

    This class provides methods to interact with the SignalRGB API, allowing users
    to retrieve, apply, and manage lighting effects and layouts.
    """

    def __init__(
        self, host: str = "localhost", port: int = DEFAULT_PORT, timeout: float = 10.0
    ):
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
        self._session = requests.Session()
        self._timeout = timeout

    @contextmanager
    def _request_context(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> Iterator[Dict[str, Any]]:
        """Context manager for making API requests.

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
            SignalRGBException: For any other unexpected errors.
        """
        url = f"{self._base_url}{endpoint}"
        debug = os.getenv("SIGNALRGB_DEBUG", "0") == "1"

        if debug:
            print(f"DEBUG: Request URL: {url}")
            print(f"DEBUG: Request Method: {method}")
            print(f"DEBUG: Request Headers: {kwargs.get('headers', {})}")
            print(f"DEBUG: Request Data: {kwargs.get('json', {})}")

        try:
            response = self._session.request(
                method, url, timeout=self._timeout, **kwargs
            )
            response.raise_for_status()

            if debug:
                print(f"DEBUG: Response Status Code: {response.status_code}")
                print(f"DEBUG: Response Headers: {response.headers}")
                print(f"DEBUG: Response Content: {response.text}")

            yield response.json()
        except requests.ConnectionError as e:
            raise ConnectionError(
                f"Failed to connect to SignalRGB API: {e}", Error(title=str(e))
            )
        except Timeout:
            raise ConnectionError("Request timed out", Error(title="Request Timeout"))
        except requests.HTTPError as e:
            if e.response is not None:
                error_data = e.response.json().get("errors", [{}])[0]
                error = Error.from_dict(error_data)
                raise APIError(f"HTTP error occurred: {e}", error)
            raise APIError(f"HTTP error occurred: {e}", Error(title=str(e)))
        except RequestException as e:
            raise APIError(
                f"An error occurred while making the request: {e}", Error(title=str(e))
            )
        except APIError as e:
            raise e
        except Exception as e:
            raise SignalRGBException(f"An unexpected error occurred: {e}")

    @lru_cache(maxsize=1)
    def get_effects(self) -> List[Effect]:
        """List available effects.

        Returns:
            List[Effect]: A list of available effects.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an error retrieving the effects.
            SignalRGBException: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> effects = client.get_effects()
            >>> print(f"Found {len(effects)} effects")
        """
        with self._request_context("GET", f"{LIGHTING_V1}/effects") as data:
            response = EffectListResponse.from_dict(data)
            self._ensure_response_ok(response)
            effects = response.data
            if effects is None or effects.items is None:
                raise APIError("No effects data in the response")
            return effects.items

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
            SignalRGBException: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> effect = client.get_effect("example_effect_id")
            >>> print(f"Effect name: {effect.attributes.name}")
        """
        try:
            with self._request_context(
                "GET", f"{LIGHTING_V1}/effects/{effect_id}"
            ) as data:
                response = EffectDetailsResponse.from_dict(data)
                self._ensure_response_ok(response)
                if response.data is None:
                    raise APIError("No effect data in the response")
                return response.data
        except APIError as e:
            if e.error and e.error.code == "not_found":
                raise NotFoundError(f"Effect with ID '{effect_id}' not found", e.error)
            raise

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
            SignalRGBException: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> effect = client.get_effect_by_name("Rainbow Wave")
            >>> print(f"Effect ID: {effect.id}")
        """
        effect = next(
            (e for e in self.get_effects() if e.attributes.name == effect_name),
            None,
        )
        if effect is None:
            raise NotFoundError(f"Effect '{effect_name}' not found")
        return self.get_effect(effect.id)

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
            SignalRGBException: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> current_effect = client.get_current_effect()
            >>> print(f"Current effect: {current_effect.attributes.name}")
        """
        state = self._get_current_state()
        if state.attributes is None:
            raise APIError("No current effect data in the response")
        return self.get_effect(state.id)

    def _get_current_state(self) -> CurrentStateHolder:
        """Get the current state of the SignalRGB instance.

        Returns:
            CurrentStateHolder: The current state of the SignalRGB instance.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBException: For any other unexpected errors.
        """
        with self._request_context("GET", LIGHTING_V1) as data:
            response = CurrentStateResponse.from_dict(data)
            self._ensure_response_ok(response)
            if response.data is None:
                raise APIError("No current state data in the response")
            return response.data

    @property
    def brightness(self) -> int:
        """Get or set the current brightness level.

        Returns:
            int: The current brightness level (0-100).

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBException: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> print(f"Current brightness: {client.brightness}")
            >>> client.brightness = 75
            >>> print(f"New brightness: {client.brightness}")
        """
        return self._get_current_state().attributes.global_brightness

    @brightness.setter
    def brightness(self, value: int) -> None:
        with self._request_context(
            "PATCH",
            f"{LIGHTING_V1}/global_brightness",
            json={"global_brightness": value},
        ):
            pass

    @property
    def enabled(self) -> bool:
        """Get or set the current enabled state of the canvas.

        Returns:
            bool: The current enabled state.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBException: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> print(f"Canvas enabled: {client.enabled}")
            >>> client.enabled = False
            >>> print(f"Canvas now disabled: {not client.enabled}")
        """
        return self._get_current_state().attributes.enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        with self._request_context(
            "PATCH", f"{LIGHTING_V1}/enabled", json={"enabled": value}
        ):
            pass

    def apply_effect(self, effect_id: str) -> None:
        """Apply an effect.

        Args:
            effect_id (str): The ID of the effect to apply.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBException: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> client.apply_effect("example_effect_id")
            >>> print("Effect applied successfully")
        """
        with self._request_context(
            "POST", f"{LIGHTING_V1}/effects/{effect_id}/apply"
        ) as data:
            response = SignalRGBResponse.from_dict(data)
            self._ensure_response_ok(response)

    def apply_effect_by_name(self, effect_name: str) -> None:
        """Apply an effect by name.

        Args:
            effect_name: The name of the effect to apply.

        Raises:
            NotFoundError: If the effect with the given name is not found.
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBException: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> client.apply_effect_by_name("Rainbow Wave")
            >>> print("Effect applied successfully")
        """
        effect = self.get_effect_by_name(effect_name)
        with self._request_context("POST", effect.links.apply):
            pass

    def get_effect_presets(self, effect_id: str) -> List[EffectPreset]:
        """Get presets for a specific effect.

        Args:
            effect_id (str): The ID of the effect to retrieve presets for.

        Returns:
            List[EffectPreset]: A list of effect presets.

        Raises:
            NotFoundError: If the effect with the given ID is not found.
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBException: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> presets = client.get_effect_presets("example_effect_id")
            >>> for preset in presets:
            ...     print(f"Preset ID: {preset.id}, Name: {preset.name}")
        """
        try:
            with self._request_context(
                "GET", f"{LIGHTING_V1}/effects/{effect_id}/presets"
            ) as data:
                response = EffectPresetListResponse.from_dict(data)
                self._ensure_response_ok(response)
                if response.data is None or response.data.items is None:
                    raise APIError("No preset data in the response")
                return response.data.items
        except APIError as e:
            if e.error and e.error.code == "not_found":
                raise NotFoundError(f"Effect with ID '{effect_id}' not found", e.error)
            raise

    def apply_effect_preset(self, effect_id: str, preset_id: str) -> None:
        """Apply a preset for a specific effect.

        Args:
            effect_id (str): The ID of the effect to apply the preset to.
            preset_id (str): The ID of the preset to apply.

        Raises:
            NotFoundError: If the effect with the given ID is not found.
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBException: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> client.apply_effect_preset("example_effect_id", "My Fancy Preset 1")
            >>> print("Preset applied successfully")
        """
        try:
            with self._request_context(
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
                )
            raise

    def get_next_effect(self) -> Optional[Effect]:
        """Get information about the next effect in history.

        Returns:
            Optional[Effect]: The next effect if available, None otherwise.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBException: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> next_effect = client.get_next_effect()
            >>> if next_effect:
            ...     print(f"Next effect: {next_effect.attributes.name}")
            ... else:
            ...     print("No next effect available")
        """
        try:
            with self._request_context("GET", f"{LIGHTING_V1}/next") as data:
                response = EffectDetailsResponse.from_dict(data)
                self._ensure_response_ok(response)
                return response.data
        except APIError as e:
            if e.error and e.error.code == "409":
                return None
            raise

    def apply_next_effect(self) -> Effect:
        """Apply the next effect in history or a random effect if there's no next effect.

        Returns:
            Effect: The newly applied effect.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBException: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> new_effect = client.apply_next_effect()
            >>> print(f"Applied effect: {new_effect.attributes.name}")
        """
        with self._request_context("POST", f"{LIGHTING_V1}/next") as data:
            response = EffectDetailsResponse.from_dict(data)
            self._ensure_response_ok(response)
            if response.data is None:
                raise APIError("No effect data in the response")
            return response.data

    def get_previous_effect(self) -> Optional[Effect]:
        """Get information about the previous effect in history.

        Returns:
            Optional[Effect]: The previous effect if available, None otherwise.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBException: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> prev_effect = client.get_previous_effect()
            >>> if prev_effect:
            ...     print(f"Previous effect: {prev_effect.attributes.name}")
            ... else:
            ...     print("No previous effect available")
        """
        try:
            with self._request_context("GET", f"{LIGHTING_V1}/previous") as data:
                response = EffectDetailsResponse.from_dict(data)
                self._ensure_response_ok(response)
                return response.data
        except APIError as e:
            if e.error and e.error.code == "409":
                return None
            raise

    def apply_previous_effect(self) -> Effect:
        """Apply the previous effect in history.

        Returns:
            Effect: The newly applied effect.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBException: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> new_effect = client.apply_previous_effect()
            >>> print(f"Applied effect: {new_effect.attributes.name}")
        """
        with self._request_context("POST", f"{LIGHTING_V1}/previous") as data:
            response = EffectDetailsResponse.from_dict(data)
            self._ensure_response_ok(response)
            if response.data is None:
                raise APIError("No effect data in the response")
            return response.data

    def apply_random_effect(self) -> Effect:
        """Apply a random effect.

        Returns:
            Effect: The newly applied random effect.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBException: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> random_effect = client.apply_random_effect()
            >>> print(f"Applied random effect: {random_effect.attributes.name}")
        """
        with self._request_context("POST", f"{LIGHTING_V1}/shuffle") as data:
            response = EffectDetailsResponse.from_dict(data)
            self._ensure_response_ok(response)
            if response.data is None:
                raise APIError("No effect data in the response")
            return response.data

    @property
    def current_layout(self) -> Layout:
        """Get the current layout.

        Returns:
            Layout: The currently active layout.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBException: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> current_layout = client.current_layout
            >>> print(f"Current layout: {current_layout.id}")
        """
        with self._request_context("GET", f"{SCENES_V1}/current_layout") as data:
            response = CurrentLayoutResponse.from_dict(data)
            self._ensure_response_ok(response)
            if response.data is None or response.data.current_layout is None:
                raise APIError("No current layout data in the response")
            return response.data.current_layout

    @current_layout.setter
    def current_layout(self, layout_id: str) -> None:
        """Set the current layout.

        Args:
            layout_id: The ID of the layout to set as current.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBException: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> client.current_layout = "My Layout 1"
            >>> print(f"New current layout: {client.current_layout.id}")
        """
        with self._request_context(
            "PATCH", f"{SCENES_V1}/current_layout", json={"layout": layout_id}
        ) as data:
            response = CurrentLayoutResponse.from_dict(data)
            self._ensure_response_ok(response)
            if response.data is None or response.data.current_layout is None:
                raise APIError("No current layout data in the response")
            if response.data.current_layout.id != layout_id:
                raise APIError(f"Failed to set layout to '{layout_id}'")

    def get_layouts(self) -> List[Layout]:
        """Get all available layouts.

        Returns:
            List[Layout]: A list of all available layouts.

        Raises:
            ConnectionError: If there's a connection error.
            APIError: If there's an API error.
            SignalRGBException: For any other unexpected errors.

        Example:
            >>> client = SignalRGBClient()
            >>> layouts = client.get_layouts()
            >>> for layout in layouts:
            ...     print(f"Layout: {layout.id}")
        """
        with self._request_context("GET", f"{SCENES_V1}/layouts") as data:
            response = LayoutListResponse.from_dict(data)
            self._ensure_response_ok(response)
            if "data" not in data or "items" not in data["data"]:
                raise APIError("No layouts data in the response")
            return [Layout.from_dict(item) for item in data["data"]["items"]]

    @staticmethod
    def _ensure_response_ok(response: SignalRGBResponse) -> None:
        """Ensure the response status is 'ok'.

        Args:
            response: The response to check.

        Raises:
            APIError: If the response status is not 'ok'.
        """
        if response.status != "ok":
            error = response.errors[0] if response.errors else None
            raise APIError(f"API returned non-OK status: {response.status}", error)

    def refresh_effects(self) -> None:
        """Refresh the cached effects.

        This method clears the cache for the get_effects method, forcing a fresh
        retrieval of effects on the next call.

        Example:
            >>> client = SignalRGBClient()
            >>> client.refresh_effects()
            >>> fresh_effects = client.get_effects()
        """
        self.get_effects.cache_clear()

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
