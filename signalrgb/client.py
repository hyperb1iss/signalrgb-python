"""Simple client for interacting with the SignalRGB API."""

import requests
from typing import Dict, List, Optional
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

        if error is not None:
            self.code = error.code
            self.title = error.title
            self.detail = error.detail


class SignalRGBClient:
    """Client for interacting with the SignalRGB API."""

    def __init__(self, host: str = "localhost", port: int = DEFAULT_PORT):
        """Initialize the SignalRGBClient.

        Args:
            host (str): The host of the SignalRGB API. Defaults to 'localhost'.
            port (int): The port of the SignalRGB API. Defaults to 16038.
        """
        self._base_url = f"http://{host}:{port}/"
        self._session = requests.Session()
        self._cached_effects: Optional[List[Effect]] = None
        self._effects_by_name: Dict[str, Effect] = {}

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make a request to the API."""
        url = f"{self._base_url}/{endpoint}"
        response = self._session.request(method, url, **kwargs)
        response.raise_for_status()
        return response

    def _ensure_cached(self) -> None:
        """Ensure the effects are cached."""
        if self._cached_effects is None:
            self.refresh_effects()

    def refresh_effects(self) -> None:
        """Refresh the cached effects."""
        response = self._request("GET", "api/v1/lighting/effects")
        effects = EffectListResponse.model_validate(response.json())
        self._ensure_response_ok(effects)
        self._effects_by_name.clear()
        for effect in effects.data.items:
            self._effects_by_name[effect.attributes.name] = effect
        self._cached_effects = effects.data.items

    def get_effects(self) -> List[Effect]:
        """List available effects."""
        self._ensure_cached()
        return self._cached_effects

    def get_effect(self, effect_id: str) -> Effect:
        """Get details of a specific effect."""
        response = self._request("GET", f"api/v1/lighting/effects/{effect_id}")
        effect = EffectDetailsResponse.model_validate(response.json())
        self._ensure_response_ok(effect)
        return effect.data

    def get_effect_by_name(self, effect_name: str) -> Effect:
        """Get details of a specific effect by name."""
        self._ensure_cached()
        cached = self._effects_by_name.get(effect_name)
        if cached is None:
            raise SignalRGBException(Error(title=f"Effect \"{effect_name}\" not found"))
        return self.get_effect(cached.id)

    def get_current_effect(self) -> Effect:
        """Get the current effect."""
        response = self._request("GET", "api/v1/lighting")
        effect = EffectDetailsResponse.model_validate(response.json())
        self._ensure_response_ok(effect)
        return effect.data

    def apply_effect(self, effect_id: str) -> None:
        """Apply an effect."""
        response = self._request("POST", f"api/v1/effects/{effect_id}/apply")
        result = SignalRGBResponse.model_validate(response.json())
        self._ensure_response_ok(result)

    def apply_effect_by_name(self, effect_name: str) -> None:
        """Apply an effect by name."""
        self._ensure_cached()
        cached = self._effects_by_name.get(effect_name)
        if cached is None:
            raise SignalRGBException(Error(title=f"Effect \"{effect_name}\" not found"))
        response = self._request("POST", cached.links.apply)
        result = SignalRGBResponse.model_validate(response.json())
        self._ensure_response_ok(result)

    def _ensure_response_ok(self, response: SignalRGBResponse) -> None:
        """Ensure the response is ok."""
        if response.status != "ok":
            raise SignalRGBException(response.errors[0] if response.errors else None)