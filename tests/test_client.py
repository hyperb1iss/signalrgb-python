import unittest
from unittest.mock import Mock, patch

import pytest
import requests
from requests.exceptions import ConnectionError as RequestsConnectionError, Timeout

from signalrgb.client import (
    APIError,
    ConnectionError,
    NotFoundError,
    SignalRGBClient,
    SignalRGBError,
    SignalRGBException,
)
from signalrgb.model import (
    Attributes,
    CurrentLayoutHolder,
    CurrentLayoutResponse,
    CurrentState,
    CurrentStateHolder,
    Effect,
    EffectDetailsResponse,
    EffectList,
    EffectListResponse,
    EffectPreset,
    EffectPresetList,
    EffectPresetListResponse,
    Error,
    Layout,
    LayoutListResponse,
    Links,
    SignalRGBResponse,
)


class BaseSignalRGBClientTest(unittest.TestCase):
    """Base class for SignalRGBClient tests."""

    def setUp(self):
        """Set up the client for each test."""
        self.client = SignalRGBClient("testhost", 12345)

    def tearDown(self):
        """Clean up after each test."""

    def assert_request_called_with(self, mock_request, method, url, **kwargs):
        """Helper method to assert that a request was called with specific parameters."""
        mock_request.assert_called_with(method, url, timeout=10.0, **kwargs)


# pylint: disable=too-many-public-methods
class TestSignalRGBClient(BaseSignalRGBClientTest):
    """Tests for the SignalRGBClient class."""

    @patch("requests.Session.request")
    def test_get_effects(self, mock_request):
        """Test getting a list of effects."""
        mock_response = Mock()
        effects = [
            Effect(
                id="effect1",
                type="lighting",
                attributes=Attributes(name="Effect 1"),
                links=Links(),
            ),
            Effect(
                id="effect2",
                type="lighting",
                attributes=Attributes(name="Effect 2"),
                links=Links(),
            ),
        ]
        response = EffectListResponse(
            api_version="1.0",
            id=1,
            method="GET",
            status="ok",
            data=EffectList(items=effects),
        )
        mock_response.json.return_value = response.to_dict()
        mock_request.return_value = mock_response

        effects = self.client.get_effects()
        assert len(effects) == 2
        assert effects[0].id == "effect1"
        assert effects[1].id == "effect2"

    @patch("requests.Session.request")
    def test_get_effect(self, mock_request):
        """Test getting a specific effect by ID."""
        mock_response = Mock()
        effect = Effect(
            id="effect1",
            type="lighting",
            attributes=Attributes(name="Effect 1"),
            links=Links(),
        )
        response = EffectDetailsResponse(
            api_version="1.0",
            id=1,
            method="GET",
            status="ok",
            data=effect,
        )
        mock_response.json.return_value = response.to_dict()
        mock_request.return_value = mock_response

        effect = self.client.get_effect("effect1")
        assert effect.id == "effect1"
        assert effect.attributes.name == "Effect 1"

    @patch("requests.Session.request")
    def test_get_effect_by_name(self, mock_request):
        """Test getting a specific effect by name."""
        mock_response_get_effects = Mock()
        effects = [
            Effect(
                id="effect1",
                type="lighting",
                attributes=Attributes(name="Test Effect 1"),
                links=Links(),
            )
        ]
        response_get_effects = EffectListResponse(
            api_version="1.0",
            id=1,
            method="GET",
            status="ok",
            data=EffectList(items=effects),
        )
        mock_response_get_effects.json.return_value = response_get_effects.to_dict()

        mock_response_get_effect = Mock()
        effect = Effect(
            id="effect1",
            type="lighting",
            attributes=Attributes(name="Test Effect 1"),
            links=Links(),
        )
        response_get_effect = EffectDetailsResponse(
            api_version="1.0",
            id=2,
            method="GET",
            status="ok",
            data=effect,
        )
        mock_response_get_effect.json.return_value = response_get_effect.to_dict()

        mock_request.side_effect = [
            mock_response_get_effects,
            mock_response_get_effect,
        ]

        effect = self.client.get_effect_by_name("Test Effect 1")
        assert effect.id == "effect1"
        assert effect.attributes.name == "Test Effect 1"

    @patch("requests.Session.request")
    def test_get_current_effect(self, mock_request):
        """Test getting the current effect."""
        mock_response_current_state = Mock()
        current_state = CurrentStateHolder(
            attributes=CurrentState(name="Current Effect", enabled=True, global_brightness=50),
            id="current_state",
            links=Links(),
            type="current_state",
        )
        response_current_state = EffectDetailsResponse(
            api_version="1.0",
            id=1,
            method="GET",
            status="ok",
            data=current_state,
        )
        mock_response_current_state.json.return_value = response_current_state.to_dict()

        mock_response_get_effect = Mock()
        effect = Effect(
            id="current_state",
            type="lighting",
            attributes=Attributes(name="Current Effect"),
            links=Links(),
        )
        response_get_effect = EffectDetailsResponse(
            api_version="1.0",
            id=2,
            method="GET",
            status="ok",
            data=effect,
        )
        mock_response_get_effect.json.return_value = response_get_effect.to_dict()

        mock_request.side_effect = [
            mock_response_current_state,
            mock_response_get_effect,
        ]

        effect = self.client.get_current_effect()
        assert effect.id == "current_state"
        assert effect.attributes.name == "Current Effect"

    @patch("requests.Session.request")
    def test_apply_effect(self, mock_request):
        """Test applying an effect by ID."""
        mock_response = Mock()
        response = SignalRGBResponse(
            api_version="1.0",
            id=1,
            method="POST",
            status="ok",
        )
        mock_response.json.return_value = response.to_dict()
        mock_request.return_value = mock_response

        self.client.apply_effect("effect1")
        self.assert_request_called_with(
            mock_request,
            "POST",
            "http://testhost:12345/api/v1/lighting/effects/effect1/apply",
        )

    @patch("requests.Session.request")
    def test_apply_effect_by_name(self, mock_request):
        """Test applying an effect by name."""
        mock_response_get_effects = Mock()
        effects = [
            Effect(
                id="effect1",
                type="lighting",
                attributes=Attributes(name="Test Effect 1"),
                links=Links(apply="/api/v1/effects/effect1/apply"),
            )
        ]
        response_get_effects = EffectListResponse(
            api_version="1.0",
            id=1,
            method="GET",
            status="ok",
            data=EffectList(items=effects),
        )
        mock_response_get_effects.json.return_value = response_get_effects.to_dict()

        mock_response_get_effect = Mock()
        effect = Effect(
            id="effect1",
            type="lighting",
            attributes=Attributes(name="Test Effect 1"),
            links=Links(apply="/api/v1/effects/effect1/apply"),
        )
        response_get_effect = EffectDetailsResponse(
            api_version="1.0",
            id=2,
            method="GET",
            status="ok",
            data=effect,
        )
        mock_response_get_effect.json.return_value = response_get_effect.to_dict()

        mock_response_apply = Mock()
        response_apply = SignalRGBResponse(
            api_version="1.0",
            id=3,
            method="POST",
            status="ok",
        )
        mock_response_apply.json.return_value = response_apply.to_dict()

        mock_request.side_effect = [
            mock_response_get_effects,
            mock_response_get_effect,
            mock_response_apply,
        ]

        self.client.apply_effect_by_name("Test Effect 1")

        assert mock_request.call_count == 3

        self.assert_request_called_with(mock_request, "POST", "http://testhost:12345/api/v1/effects/effect1/apply")

    @patch("requests.Session.request")
    def test_connection_error(self, mock_request):
        """Test handling connection errors."""
        mock_request.side_effect = RequestsConnectionError("Connection failed")

        with pytest.raises(ConnectionError) as context:
            self.client.get_effects()

        assert "Failed to connect to SignalRGB API" in str(context.value)

    @patch("requests.Session.request")
    def test_generic_request_exception(self, mock_request):
        """Test handling generic request exceptions."""
        mock_request.side_effect = ValueError("Unexpected error")

        with pytest.raises(SignalRGBError) as context:
            self.client.get_effects()

        assert "An unexpected error occurred" in str(context.value)

    @patch("requests.Session.request")
    def test_timeout_error(self, mock_request):
        """Test handling timeout errors."""
        mock_request.side_effect = Timeout("Request timed out")

        with pytest.raises(ConnectionError) as context:
            self.client.get_effects()

        assert "Request timed out" in str(context.value)

    @patch("requests.Session.request")
    def test_brightness(self, mock_request):
        """Test setting and getting the brightness level."""
        mock_response = Mock()
        response = SignalRGBResponse(
            api_version="1.0",
            id=1,
            method="PATCH",
            status="ok",
        )
        mock_response.json.return_value = response.to_dict()
        mock_request.return_value = mock_response

        self.client.brightness = 50
        self.assert_request_called_with(
            mock_request,
            "PATCH",
            "http://testhost:12345/api/v1/lighting/global_brightness",
            json={"global_brightness": 50},
        )

        mock_response.json.return_value = {
            "api_version": "1.0",
            "id": 1,
            "method": "GET",
            "status": "ok",
            "data": {
                "attributes": {"global_brightness": 50, "enabled": False, "name": None},
                "id": "current_state",
                "links": {},
                "type": "current_state",
            },
        }
        brightness = self.client.brightness
        assert brightness == 50

    @patch("requests.Session.request")
    def test_enabled(self, mock_request):
        """Test setting and getting the enabled state."""
        mock_response = Mock()
        response = SignalRGBResponse(
            api_version="1.0",
            id=1,
            method="PATCH",
            status="ok",
        )
        mock_response.json.return_value = response.to_dict()
        mock_request.return_value = mock_response

        self.client.enabled = True
        self.assert_request_called_with(
            mock_request,
            "PATCH",
            "http://testhost:12345/api/v1/lighting/enabled",
            json={"enabled": True},
        )

        mock_response.json.return_value = {
            "api_version": "1.0",
            "id": 1,
            "method": "GET",
            "status": "ok",
            "data": {
                "attributes": {"global_brightness": 0, "enabled": True, "name": None},
                "id": "current_state",
                "links": {},
                "type": "current_state",
            },
        }
        enabled = self.client.enabled
        assert enabled

    @patch("requests.Session.request")
    def test_ensure_response_ok(self, mock_request):
        """Test the ensure_response_ok method."""
        # Set up the mock response with error status
        mock_response = Mock()
        error_response = SignalRGBResponse(
            api_version="1.0",
            id=1,
            method="GET",
            status="error",
            errors=[Error(code="404", title="Not Found")],
        )
        mock_response.json.return_value = error_response.to_dict()
        mock_request.return_value = mock_response

        # First get the response data using the context manager
        with self.client._request_context("GET", "/api/v1/lighting/effects") as response_data:
            response = SignalRGBResponse.from_dict(response_data)

            # Then test the ensure_response_ok method separately with pytest.raises
            with pytest.raises(APIError) as context:
                self.client._ensure_response_ok(response)

        assert "API returned non-OK status" in str(context.value)

    @patch("requests.Session.request")
    def test_request_success(self, mock_request):
        """Test a successful request."""
        mock_response = Mock()
        response = SignalRGBResponse(
            api_version="1.0",
            id=1,
            method="GET",
            status="ok",
        )
        mock_response.json.return_value = response.to_dict()
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        with self.client._request_context("GET", "/api/v1/lighting/effects") as response:
            assert response["status"] == "ok"

    @patch("requests.Session.request")
    def test_request_connection_error(self, mock_request):
        """Test handling connection errors in requests."""
        mock_request.side_effect = RequestsConnectionError("Connection failed")

        with (
            pytest.raises(ConnectionError) as context,
            self.client._request_context("GET", "/api/v1/lighting/effects") as _,
        ):
            pass

        assert "Failed to connect to SignalRGB API" in str(context.value)

    @patch("requests.Session.request")
    def test_request_timeout(self, mock_request):
        """Test handling timeout errors in requests."""
        mock_request.side_effect = Timeout("Request timed out")

        with (
            pytest.raises(ConnectionError) as context,
            self.client._request_context("GET", "/api/v1/lighting/effects") as _,
        ):
            pass

        assert "Request timed out" in str(context.value)

    @patch("requests.Session.request")
    def test_request_http_error(self, mock_request):
        """Test handling HTTP errors in requests."""
        mock_response = Mock()
        error_response = SignalRGBResponse(
            api_version="1.0",
            id=1,
            method="GET",
            status="error",
            errors=[Error(code="404", title="Not Found")],
        )
        mock_response.json.return_value = error_response.to_dict()
        mock_response.raise_for_status.side_effect = requests.HTTPError("HTTP error")
        mock_request.return_value = mock_response

        with pytest.raises(APIError) as context, self.client._request_context("GET", "/api/v1/lighting/effects") as _:
            pass

        assert "HTTP error occurred" in str(context.value)

    @patch("requests.Session.request")
    def test_request_generic_error(self, mock_request):
        """Test handling generic errors in requests."""
        mock_request.side_effect = ValueError("Unexpected error")

        with (
            pytest.raises(SignalRGBError) as context,
            self.client._request_context("GET", "/api/v1/lighting/effects") as _,
        ):
            pass

        assert "unexpected error" in str(context.value)

    @patch("requests.Session.request")
    def test_get_effects_error(self, mock_request):
        """Test handling errors when getting effects."""
        mock_response = Mock()
        error_response = SignalRGBResponse(
            api_version="1.0",
            id=1,
            method="GET",
            status="error",
            errors=[Error(code="500", title="Internal Server Error")],
        )
        mock_response.json.return_value = error_response.to_dict()
        mock_request.return_value = mock_response

        with pytest.raises(APIError) as context:
            self.client.get_effects()

        assert "API returned non-OK status" in str(context.value)

    @patch("requests.Session.request")
    def test_get_effect_error(self, mock_request):
        """Test handling errors when getting a specific effect."""
        mock_response = Mock()
        error_response = SignalRGBResponse(
            api_version="1.0",
            id=1,
            method="GET",
            status="error",
            errors=[Error(code="404", title="Not Found")],
        )
        mock_response.json.return_value = error_response.to_dict()
        mock_request.return_value = mock_response

        with pytest.raises(APIError) as context:
            self.client.get_effect("nonexistent_effect")

        assert "API returned non-OK status" in str(context.value)

    @patch("requests.Session.request")
    def test_get_effect_by_name_error(self, mock_request):
        """Test handling errors when getting an effect by name."""
        mock_response_get_effects = Mock()
        response_get_effects = EffectListResponse(
            api_version="1.0",
            id=1,
            method="GET",
            status="ok",
            data=EffectList(items=[]),
        )
        mock_response_get_effects.json.return_value = response_get_effects.to_dict()

        mock_request.return_value = mock_response_get_effects

        with pytest.raises(NotFoundError) as context:
            self.client.get_effect_by_name("Nonexistent Effect")

        assert "Effect 'Nonexistent Effect' not found" in str(context.value)

    @patch("requests.Session.request")
    def test_get_current_effect_error(self, mock_request):
        """Test handling errors when getting the current effect."""
        mock_response_current_state = Mock()
        error_response = SignalRGBResponse(
            api_version="1.0",
            id=1,
            method="GET",
            status="error",
            errors=[Error(code="500", title="Internal Server Error")],
        )
        mock_response_current_state.json.return_value = error_response.to_dict()
        mock_request.return_value = mock_response_current_state

        with pytest.raises(APIError) as context:
            self.client.get_current_effect()

        assert "API returned non-OK status" in str(context.value)

    @patch("requests.Session.request")
    def test_apply_effect_error(self, mock_request):
        """Test handling errors when applying an effect."""
        mock_response = Mock()
        error_response = SignalRGBResponse(
            api_version="1.0",
            id=1,
            method="POST",
            status="error",
            errors=[Error(code="404", title="Not Found")],
        )
        mock_response.json.return_value = error_response.to_dict()
        mock_request.return_value = mock_response

        with pytest.raises(SignalRGBException) as context:
            self.client.apply_effect("nonexistent_effect")

        assert "API returned non-OK status" in str(context.value)

    @patch("requests.Session.request")
    def test_apply_effect_by_name_error(self, mock_request):
        """Test handling errors when applying an effect by name."""
        mock_response_get_effects = Mock()
        response_get_effects = EffectListResponse(
            api_version="1.0",
            id=1,
            method="GET",
            status="ok",
            data=EffectList(items=[]),
        )
        mock_response_get_effects.json.return_value = response_get_effects.to_dict()

        mock_request.return_value = mock_response_get_effects

        with pytest.raises(NotFoundError) as context:
            self.client.apply_effect_by_name("Nonexistent Effect")

        assert "Effect 'Nonexistent Effect' not found" in str(context.value)

    @patch("requests.Session.request")
    def test_refresh_effects(self, mock_request):
        """Test refreshing the cached effects."""
        effects1 = [
            Effect(
                id="effect1",
                type="lighting",
                attributes=Attributes(name="Effect 1"),
                links=Links(),
            ),
            Effect(
                id="effect2",
                type="lighting",
                attributes=Attributes(name="Effect 2"),
                links=Links(),
            ),
        ]
        response1 = EffectListResponse(
            api_version="1.0",
            id=1,
            method="GET",
            status="ok",
            data=EffectList(items=effects1),
        )
        mock_request.return_value = Mock(json=Mock(return_value=response1.to_dict()))

        effects2 = [
            Effect(
                id="effect3",
                type="lighting",
                attributes=Attributes(name="Effect 3"),
                links=Links(),
            ),
            Effect(
                id="effect4",
                type="lighting",
                attributes=Attributes(name="Effect 4"),
                links=Links(),
            ),
        ]
        response2 = EffectListResponse(
            api_version="1.0",
            id=2,
            method="GET",
            status="ok",
            data=EffectList(items=effects2),
        )
        mock_request.side_effect = [
            Mock(json=Mock(return_value=response1.to_dict())),
            Mock(json=Mock(return_value=response2.to_dict())),
        ]

        effects1 = self.client.get_effects()
        assert len(effects1) == 2
        assert effects1[0].id == "effect1"
        assert effects1[1].id == "effect2"

        effects2 = self.client.get_effects()
        assert effects1 == effects2

        assert mock_request.call_count == 1

        self.client.refresh_effects()

        effects3 = self.client.get_effects()
        assert len(effects3) == 2
        assert effects3[0].id == "effect3"
        assert effects3[1].id == "effect4"

        assert mock_request.call_count == 2

    @patch("requests.Session.request")
    def test_get_current_state(self, mock_request):
        """Test getting the current state."""
        mock_response = Mock()
        current_state = CurrentStateHolder(
            attributes=CurrentState(name="Current Effect", enabled=True, global_brightness=50),
            id="current_state",
            links=Links(),
            type="current_state",
        )
        response = EffectDetailsResponse(
            api_version="1.0",
            id=1,
            method="GET",
            status="ok",
            data=current_state,
        )
        mock_response.json.return_value = response.to_dict()
        mock_request.return_value = mock_response

        state = self.client._get_current_state()
        assert state.id == "current_state"
        assert state.attributes.name == "Current Effect"

    @patch("requests.Session.request")
    def test_get_current_state_attributes(self, mock_request):
        """Test getting the current state attributes."""
        mock_response = Mock()
        current_state = CurrentStateHolder(
            attributes=CurrentState(name="Current Effect", enabled=True, global_brightness=50),
            id="current_state",
            links=Links(),
            type="current_state",
        )
        response = EffectDetailsResponse(
            api_version="1.0",
            id=1,
            method="GET",
            status="ok",
            data=current_state,
        )
        mock_response.json.return_value = response.to_dict()
        mock_request.return_value = mock_response

        attributes = self.client._get_current_state().attributes
        assert attributes.name == "Current Effect"
        assert attributes.enabled
        assert attributes.global_brightness == 50

    @patch("requests.Session.request")
    def test_get_effect_presets(self, mock_request):
        """Test getting presets for a specific effect."""
        mock_response = Mock()
        presets = [
            EffectPreset(id="preset1", type="preset"),
            EffectPreset(id="preset2", type="preset"),
        ]
        response = EffectPresetListResponse(
            api_version="1.0",
            id=1,
            method="GET",
            status="ok",
            data=EffectPresetList(id="effect1", items=presets),
        )
        mock_response.json.return_value = response.to_dict()
        mock_request.return_value = mock_response

        result = self.client.get_effect_presets("effect1")
        assert len(result) == 2
        assert result[0].id == "preset1"
        assert result[1].id == "preset2"
        assert result[0].type == "preset"
        assert result[1].type == "preset"

    @patch("requests.Session.request")
    def test_apply_effect_preset(self, mock_request):
        """Test applying a preset for a specific effect."""
        mock_response = Mock()
        response = SignalRGBResponse(
            api_version="1.0",
            id=1,
            method="PATCH",
            status="ok",
        )
        mock_response.json.return_value = response.to_dict()
        mock_request.return_value = mock_response

        self.client.apply_effect_preset("effect1", "preset1")
        self.assert_request_called_with(
            mock_request,
            "PATCH",
            "http://testhost:12345/api/v1/lighting/effects/effect1/presets",
            json={"preset": "preset1"},
        )

    @patch("requests.Session.request")
    def test_get_next_effect(self, mock_request):
        """Test getting the next effect in history."""
        mock_response = Mock()
        effect = Effect(
            id="next_effect",
            type="lighting",
            attributes=Attributes(name="Next Effect"),
            links=Links(),
        )
        response = EffectDetailsResponse(
            api_version="1.0",
            id=1,
            method="GET",
            status="ok",
            data=effect,
        )
        mock_response.json.return_value = response.to_dict()
        mock_request.return_value = mock_response

        next_effect = self.client.get_next_effect()
        assert next_effect.id == "next_effect"
        assert next_effect.attributes.name == "Next Effect"

    @patch("requests.Session.request")
    def test_apply_next_effect(self, mock_request):
        """Test applying the next effect in history."""
        mock_response = Mock()
        effect = Effect(
            id="next_effect",
            type="lighting",
            attributes=Attributes(name="Next Effect"),
            links=Links(),
        )
        response = EffectDetailsResponse(
            api_version="1.0",
            id=1,
            method="POST",
            status="ok",
            data=effect,
        )
        mock_response.json.return_value = response.to_dict()
        mock_request.return_value = mock_response

        applied_effect = self.client.apply_next_effect()
        assert applied_effect.id == "next_effect"
        assert applied_effect.attributes.name == "Next Effect"

    @patch("requests.Session.request")
    def test_get_previous_effect(self, mock_request):
        """Test getting the previous effect in history."""
        mock_response = Mock()
        effect = Effect(
            id="previous_effect",
            type="lighting",
            attributes=Attributes(name="Previous Effect"),
            links=Links(),
        )
        response = EffectDetailsResponse(
            api_version="1.0",
            id=1,
            method="GET",
            status="ok",
            data=effect,
        )
        mock_response.json.return_value = response.to_dict()
        mock_request.return_value = mock_response

        previous_effect = self.client.get_previous_effect()
        assert previous_effect.id == "previous_effect"
        assert previous_effect.attributes.name == "Previous Effect"

    @patch("requests.Session.request")
    def test_apply_previous_effect(self, mock_request):
        """Test applying the previous effect in history."""
        mock_response = Mock()
        effect = Effect(
            id="previous_effect",
            type="lighting",
            attributes=Attributes(name="Previous Effect"),
            links=Links(),
        )
        response = EffectDetailsResponse(
            api_version="1.0",
            id=1,
            method="POST",
            status="ok",
            data=effect,
        )
        mock_response.json.return_value = response.to_dict()
        mock_request.return_value = mock_response

        applied_effect = self.client.apply_previous_effect()
        assert applied_effect.id == "previous_effect"
        assert applied_effect.attributes.name == "Previous Effect"

    @patch("requests.Session.request")
    def test_apply_random_effect(self, mock_request):
        """Test applying a random effect."""
        mock_response = Mock()
        effect = Effect(
            id="random_effect",
            type="lighting",
            attributes=Attributes(name="Random Effect"),
            links=Links(),
        )
        response = EffectDetailsResponse(
            api_version="1.0",
            id=1,
            method="POST",
            status="ok",
            data=effect,
        )
        mock_response.json.return_value = response.to_dict()
        mock_request.return_value = mock_response

        random_effect = self.client.apply_random_effect()
        assert random_effect.id == "random_effect"
        assert random_effect.attributes.name == "Random Effect"

    @patch("requests.Session.request")
    def test_get_current_layout(self, mock_request):
        """Test getting the current layout."""
        mock_response = Mock()
        layout = Layout(id="current_layout", type="layout")
        response = CurrentLayoutResponse(
            api_version="1.0",
            id=1,
            method="GET",
            status="ok",
            data=CurrentLayoutHolder(current_layout=layout),
        )
        mock_response.json.return_value = response.to_dict()
        mock_request.return_value = mock_response

        current_layout = self.client.current_layout
        assert current_layout.id == "current_layout"
        assert current_layout.type == "layout"

    @patch("requests.Session.request")
    def test_set_current_layout(self, mock_request):
        """Test setting the current layout."""
        mock_response = Mock()
        layout = Layout(id="new_layout", type="layout")
        response = CurrentLayoutResponse(
            api_version="1.0",
            id=1,
            method="PATCH",
            status="ok",
            data=CurrentLayoutHolder(current_layout=layout),
        )
        mock_response.json.return_value = response.to_dict()
        mock_request.return_value = mock_response

        self.client.current_layout = "new_layout"
        self.assert_request_called_with(
            mock_request,
            "PATCH",
            "http://testhost:12345/api/v1/scenes/current_layout",
            json={"layout": "new_layout"},
        )

    @patch("requests.Session.request")
    def test_get_layouts(self, mock_request):
        """Test getting all available layouts."""
        mock_response = Mock()
        layouts = [
            Layout(id="layout1", type="layout"),
            Layout(id="layout2", type="layout"),
        ]
        response = LayoutListResponse(
            api_version="1.0",
            id=1,
            method="GET",
            status="ok",
            data={"items": [layout.to_dict() for layout in layouts]},
        )
        mock_response.json.return_value = response.to_dict()
        mock_request.return_value = mock_response

        result = self.client.get_layouts()
        assert len(result) == 2
        assert result[0].id == "layout1"
        assert result[1].id == "layout2"


if __name__ == "__main__":
    unittest.main()
