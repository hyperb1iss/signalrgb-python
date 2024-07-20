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

    def __init__(self, error: Optional[Error] = None):
        super().__init__(error.title if error else "Unknown error")
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
        response = self._session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()

    @lru_cache(maxsize=1)
    def get_effects(self) -> List[Effect]:
        """List available effects."""
        response = EffectListResponse.model_validate(self._request("GET", "/api/v1/lighting/effects"))
        self._ensure_response_ok(response)
        effects = response.data.items
        self._effects_cache = {effect.attributes.name: effect for effect in effects}
        return effects

    def get_effect(self, effect_id: str) -> Effect:
        """Get details of a specific effect."""
        response = EffectDetailsResponse.model_validate(
            self._request("GET", f"/api/v1/lighting/effects/{effect_id}")
        )
        self._ensure_response_ok(response)
        return response.data

    def get_effect_by_name(self, effect_name: str) -> Effect:
        """Get details of a specific effect by name."""
        if not self._effects_cache:
            self.get_effects()

        effect = self._effects_cache.get(effect_name)
        if effect is None:
            raise SignalRGBException(Error(title=f"Effect '{effect_name}' not found"))
        return self.get_effect(effect.id)

    def get_current_effect(self) -> Effect:
        """Get the current effect."""
        response = EffectDetailsResponse.model_validate(self._request("GET", "/api/v1/lighting"))
        self._ensure_response_ok(response)
        return response.data

    def apply_effect(self, effect_id: str) -> None:
        """Apply an effect."""
        response = SignalRGBResponse.model_validate(
            self._request("POST", f"/api/v1/effects/{effect_id}/apply")
        )
        self._ensure_response_ok(response)

    def apply_effect_by_name(self, effect_name: str) -> None:
        """Apply an effect by name."""
        effect = self.get_effect_by_name(effect_name)
        self._request("POST", effect.links.apply)

    @staticmethod
    def _ensure_response_ok(response: SignalRGBResponse) -> None:
        """Ensure the response is ok."""
        if response.status != "ok":
            raise SignalRGBException(response.errors[0] if response.errors else None)

    def refresh_effects(self) -> None:
        """Refresh the cached effects."""
        self.get_effects.cache_clear()
        self.get_effects()