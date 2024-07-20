"""Simple cient for interacting with the SignalRGB API."""

import requests
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

    def __init__(self, error: Error = None):
        super().__init__(error.title)

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
        self._cached_effects = None
        self._effects_by_name = { str: Effect }

    def _get(self, endpoint) -> requests.Response:
        """Make a get request to the API."""
        url = f"{self._base_url}/{endpoint}"
        return requests.get(url)

    def _post(self, endpoint, data: dict = {}) -> requests.Response:
        """Make a post request to the API."""
        url = f"{self._base_url}/{endpoint}"
        return requests.post(url, data)

    def _ensure_cached(self):
        """Ensure the effects are cached."""
        if self._cached_effects is None:
            self.refresh_effects()
            
    def refresh_effects(self):
        """Refresh the cached effects."""
        response = self._get("api/v1/lighting/effects")
        effects = EffectListResponse.model_validate(response.json())
        self._ensure_response_ok(effects)
        self._effects_by_name.clear()
        for effect in effects.data.items:
            self._effects_by_name[effect.attributes.name] = effect
        self._cached_effects = effects.data.items

    def get_effects(self) -> list[Effect]:
        """List available effects."""
        self._ensure_cached()
        return self._cached_effects

    def get_effect(self, effect_id: str) -> Effect:
        """Get details of a specific effect."""
        response = self._get(f"api/v1/lighting/effects/{effect_id}")
        effect = EffectDetailsResponse.model_validate(response.json())
        self._ensure_response_ok(effect)
        return effect.data
    
    def get_effect_by_name(self, effect_name: str) -> Effect:
        """Get details of a specific effect by name."""
        self._ensure_cached()
        cached = self._effects_by_name[effect_name]
        if cached is None:
            raise SignalRGBException(Error(title=f"Effect \"{effect_name}\" not found"))
        return self.get_effect(cached.id)
    
    def get_current_effect(self) -> Effect:
        """Get the current effect."""
        response = self._get("api/v1/lighting")
        effect = EffectDetailsResponse.model_validate(response.json())
        self._ensure_response_ok(effect)
        return effect.data

    def apply_effect(self, effect_id: str):
        """Apply an effect."""
        response = self._post(f"api/v1/effects/{effect_id}/apply")
        result = SignalRGBResponse.model_validate(response.json())
        self._ensure_response_ok(result)

    def apply_effect_by_name(self, effect_name: str):
        """Apply an effect by name."""
        self._ensure_cached()
        cached = self._effects_by_name[effect_name]
        if cached is None:
            raise SignalRGBException(Error(title=f"Effect \"{effect_name}\" not found"))
        response = self._post(cached.links.apply)
        result = SignalRGBResponse.model_validate(response.json())
        self._ensure_response_ok(result)
        
    def _ensure_response_ok(self, response: SignalRGBResponse):
        """Ensure the response is ok."""
        if response.status != "ok":
            raise SignalRGBException(response.errors[0].title)
