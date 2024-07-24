"""
Client for interacting with the SignalRGB API.

This module provides a client class for interacting with the SignalRGB API,
allowing users to retrieve, apply, and manage lighting effects.
"""

from __future__ import annotations

from functools import lru_cache
from typing import List, Optional, cast

import requests
from requests.exceptions import RequestException, Timeout

from .model import (
    Effect,
    EffectDetailsResponse,
    EffectListResponse,
    Error,
    SignalRGBResponse,
)


DEFAULT_PORT = 16038


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

    pass


class APIError(SignalRGBException):
    """Exception raised for API errors.

    This exception is raised when the API returns an error response.
    """

    pass


class EffectNotFoundError(SignalRGBException):
    """Exception raised when an effect is not found.

    This exception is raised when trying to retrieve or apply a non-existent effect.
    """

    pass


class SignalRGBClient:
    """Client for interacting with the SignalRGB API.

    This class provides methods to interact with the SignalRGB API, allowing users
    to retrieve, apply, and manage lighting effects.
    """

    def __init__(
        self, host: str = "localhost", port: int = DEFAULT_PORT, timeout: float = 10.0
    ):
        """Initialize the SignalRGBClient.

        Args:
            host (str): The host of the SignalRGB API. Defaults to 'localhost'.
            port (int): The port of the SignalRGB API. Defaults to 16038.
            timeout (float): The timeout for API requests in seconds. Defaults to 10.0.

        Example:
            >>> client = SignalRGBClient()
            >>> client = SignalRGBClient("192.168.1.100", 8080, 5.0)
        """
        self._base_url = f"http://{host}:{port}"
        self._session = requests.Session()
        self._timeout = timeout

    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make a request to the API and return the JSON response.

        Args:
            method (str): The HTTP method to use for the request.
            endpoint (str): The API endpoint to request.
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            dict: The JSON response from the API.

        Raises:
            ConnectionError: If there's an issue connecting to the API.
            APIError: If the API returns an error response.
            SignalRGBException: For any other request-related errors.
        """
        url = f"{self._base_url}{endpoint}"
        try:
            response = self._session.request(
                method, url, timeout=self._timeout, **kwargs
            )
            response.raise_for_status()
            return response.json()
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
            raise SignalRGBException(f"An error occurred while making the request: {e}")

    @lru_cache(maxsize=1)
    def get_effects(self) -> List[Effect]:
        """List available effects.

        Returns:
            List[Effect]: A list of available effects.

        Raises:
            APIError: If there's an error retrieving the effects.

        Example:
            >>> client = SignalRGBClient()
            >>> effects = client.get_effects()
            >>> print(f"Found {len(effects)} effects")
        """
        try:
            response_data = self._request("GET", "/api/v1/lighting/effects")
            response = EffectListResponse.from_dict(response_data)
            self._ensure_response_ok(response)
            effects = response.data
            if effects is None or effects.items is None:
                raise APIError("No effects data in the response")
            return effects.items
        except (ConnectionError, Timeout):
            raise
        except APIError:
            raise
        except Exception as e:
            raise APIError(f"Failed to retrieve effects: {e}", Error(title=str(e)))

    def get_effect(self, effect_id: str) -> Effect:
        """Get details of a specific effect.

        Args:
            effect_id (str): The ID of the effect to retrieve.

        Returns:
            Effect: The requested effect.

        Raises:
            EffectNotFoundError: If the effect with the given ID is not found.
            APIError: If there's an error retrieving the effect.

        Example:
            >>> client = SignalRGBClient()
            >>> effect = client.get_effect("example_effect_id")
            >>> print(f"Effect name: {effect.attributes.name}")
        """
        try:
            response_data = self._request(
                "GET", f"/api/v1/lighting/effects/{effect_id}"
            )
            response = EffectDetailsResponse.from_dict(response_data)
            self._ensure_response_ok(response)
            if response.data is None:
                raise APIError("No effect data in the response")
            return response.data
        except APIError as e:
            if e.error and e.error.code == "not_found":
                raise EffectNotFoundError(
                    f"Effect with ID '{effect_id}' not found", e.error
                )
            raise

    def _find_effect_by_name(self, effect_name: str) -> Optional[Effect]:
        """Find an effect by its name.

        Args:
            effect_name (str): The name of the effect to find.

        Returns:
            Optional[Effect]: The found effect, or None if not found.
        """
        return next(
            (e for e in self.get_effects() if e.attributes.name == effect_name), None
        )

    def get_effect_by_name(self, effect_name: str) -> Effect:
        """Get details of a specific effect by name.

        Args:
            effect_name (str): The name of the effect to retrieve.

        Returns:
            Effect: The requested effect.

        Raises:
            EffectNotFoundError: If the effect with the given name is not found.

        Example:
            >>> client = SignalRGBClient()
            >>> effect = client.get_effect_by_name("Rainbow Wave")
            >>> print(f"Effect ID: {effect.id}")
        """
        effect = self._find_effect_by_name(effect_name)
        if effect is None:
            raise EffectNotFoundError(f"Effect '{effect_name}' not found")

        return self.get_effect(effect.id)

    def get_current_effect(self) -> Effect:
        """Get the current effect.

        Returns:
            Effect: The currently active effect.

        Raises:
            APIError: If there's an error retrieving the current effect.

        Example:
            >>> client = SignalRGBClient()
            >>> current_effect = client.get_current_effect()
            >>> print(f"Current effect: {current_effect.attributes.name}")
        """
        try:
            response_data = self._request("GET", "/api/v1/lighting")
            response = EffectDetailsResponse.from_dict(response_data)
            self._ensure_response_ok(response)
            if response.data is None:
                raise APIError("No current effect data in the response")
            return self.get_effect(response.data.id)
        except Exception as e:
            raise APIError(
                f"Failed to retrieve current effect: {e}", Error(title=str(e))
            )

    def apply_effect(self, effect_id: str) -> None:
        """Apply an effect.

        Args:
            effect_id (str): The ID of the effect to apply.

        Raises:
            EffectNotFoundError: If the effect with the given ID is not found.
            SignalRGBException: If there's an error applying the effect.

        Example:
            >>> client = SignalRGBClient()
            >>> client.apply_effect("example_effect_id")
            >>> print("Effect applied successfully")
        """
        try:
            response_data = self._request("POST", f"/api/v1/effects/{effect_id}/apply")
            response = SignalRGBResponse.from_dict(response_data)
            self._ensure_response_ok(response)
        except APIError as e:
            if e.error and e.error.code == "not_found":
                raise EffectNotFoundError(
                    f"Effect with ID '{effect_id}' not found", e.error
                )
            raise
        except Exception as e:
            raise SignalRGBException(
                f"Failed to apply effect: {e}", Error(title=str(e))
            )

    def apply_effect_by_name(self, effect_name: str) -> None:
        """Apply an effect by name.

        Args:
            effect_name (str): The name of the effect to apply.

        Raises:
            EffectNotFoundError: If the effect with the given name is not found.
            SignalRGBException: If there's an error applying the effect.

        Example:
            >>> client = SignalRGBClient()
            >>> client.apply_effect_by_name("Rainbow Wave")
            >>> print("Effect applied successfully")
        """
        try:
            effect = self.get_effect_by_name(effect_name)
            self._request("POST", cast(str, effect.links.apply))
        except EffectNotFoundError:
            raise
        except Exception as e:
            raise SignalRGBException(
                f"Failed to apply effect '{effect_name}': {e}", Error(title=str(e))
            )

    @staticmethod
    def _ensure_response_ok(response: SignalRGBResponse) -> None:
        """Ensure the response status is 'ok'.

        Args:
            response (SignalRGBResponse): The response to check.

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
