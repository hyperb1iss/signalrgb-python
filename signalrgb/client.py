"""Simple client for interacting with the SignalRGB API."""

from __future__ import annotations

import requests
from typing import Dict, List, Optional
from functools import lru_cache
from .model import (
    EffectListResponse,
    Error,
    EffectDetailsResponse,
    Effect,
    SignalRGBResponse,
)

DEFAULT_PORT = 16038


class SignalRGBException(Exception):
    """Base exception for SignalRGB errors."""

    def __init__(self, message: str, error: Optional[Error] = None):
        super().__init__(message)
        self.error = error

    @property
    def code(self) -> Optional[str]:
        return self.error.code if self.error else None

    @property
    def title(self) -> Optional[str]:
        return self.error.title if self.error else None

    @property
    def detail(self) -> Optional[str]:
        return self.error.detail if self.error else None


class ConnectionError(SignalRGBException):
    """Exception raised for connection errors."""

    pass


class APIError(SignalRGBException):
    """Exception raised for API errors."""

    pass


class EffectNotFoundError(SignalRGBException):
    """Exception raised when an effect is not found."""

    pass


class SignalRGBClient:
    """Client for interacting with the SignalRGB API."""

    def __init__(self, host: str = "localhost", port: int = DEFAULT_PORT):
        """Initialize the SignalRGBClient.

        Args:
            host (str): The host of the SignalRGB API. Defaults to 'localhost'.
            port (int): The port of the SignalRGB API. Defaults to 16038.
        """
        self._base_url = f"http://{host}:{port}"
        self._session = requests.Session()
        self._effects_cache: Dict[str, Effect] = {}

    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make a request to the API and return the JSON response."""
        url = f"{self._base_url}{endpoint}"
        try:
            response = self._session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.ConnectionError as e:
            raise ConnectionError(f"Failed to connect to SignalRGB API: {e}")
        except requests.HTTPError as e:
            if e.response is not None:
                error_data = e.response.json().get("errors", [{}])[0]
                error = Error(**error_data)
                raise APIError(f"HTTP error occurred: {e}", error)
            raise APIError(f"HTTP error occurred: {e}", e)
        except requests.RequestException as e:
            raise SignalRGBException(f"An error occurred while making the request: {e}")

    @lru_cache(maxsize=1)
    def get_effects(self) -> List[Effect]:
        """List available effects."""
        try:
            response = EffectListResponse.model_validate(
                self._request("GET", "/api/v1/lighting/effects")
            )
            self._ensure_response_ok(response)
            effects = response.data.items
            self._effects_cache = {effect.attributes.name: effect for effect in effects}
            return effects
        except Exception as e:
            raise APIError(f"Failed to retrieve effects: {e}", e)

    def get_effect(self, effect_id: str) -> Effect:
        """Get details of a specific effect."""
        try:
            response = EffectDetailsResponse.model_validate(
                self._request("GET", f"/api/v1/lighting/effects/{effect_id}")
            )
            self._ensure_response_ok(response)
            return response.data
        except Exception as e:
            if e.error and e.error.code == "not_found":
                raise EffectNotFoundError(f"Effect with ID '{effect_id}' not found", e)
            raise

    def get_effect_by_name(self, effect_name: str) -> Effect:
        """Get details of a specific effect by name."""
        if not self._effects_cache:
            self.get_effects()

        effect = self._effects_cache.get(effect_name)
        if effect is None:
            raise EffectNotFoundError(f"Effect '{effect_name}' not found")
        return self.get_effect(effect.id)

    def get_current_effect(self) -> Effect:
        """Get the current effect."""
        try:
            response = EffectDetailsResponse.model_validate(
                self._request("GET", "/api/v1/lighting")
            )
            self._ensure_response_ok(response)
            return response.data
        except Exception as e:
            raise APIError(f"Failed to retrieve current effect: {e}", e)

    def apply_effect(self, effect_id: str) -> None:
        """Apply an effect."""
        try:
            response = SignalRGBResponse.model_validate(
                self._request("POST", f"/api/v1/effects/{effect_id}/apply")
            )
            self._ensure_response_ok(response)
        except APIError as e:
            if e.error and e.error.code == "not_found":
                raise EffectNotFoundError(f"Effect with ID '{effect_id}' not found", e)
            raise
        except Exception as e:
            raise SignalRGBException(f"Failed to apply effect: {e}", e)

    def apply_effect_by_name(self, effect_name: str) -> None:
        """Apply an effect by name."""
        try:
            effect = self.get_effect_by_name(effect_name)
            self._request("POST", effect.links.apply)
        except EffectNotFoundError:
            raise
        except Exception as e:
            raise SignalRGBException(f"Failed to apply effect '{effect_name}': {e}")

    @staticmethod
    def _ensure_response_ok(response: SignalRGBResponse) -> None:
        """Ensure the response is ok."""
        if response.status != "ok":
            error = response.errors[0] if response.errors else None
            raise APIError(f"API returned non-OK status: {response.status}", error)

    def refresh_effects(self) -> None:
        """Refresh the cached effects."""
        self.get_effects.cache_clear()
        self.get_effects()
