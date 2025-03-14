import unittest
from unittest.mock import Mock, patch

import pytest

from signalrgb.client import SignalRGBClient
from signalrgb.constants import DEFAULT_PORT
from signalrgb.exceptions import (
    APIError,
    NotFoundError,
)
from signalrgb.model import (
    Attributes,
    Effect,
    EffectPreset,
    Error,
    Layout,
    Links,
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

    def setup_method(self, method=None):
        """Set up the SignalRGBClient with a mocked AsyncSignalRGBClient."""
        # Create a mock for the AsyncSignalRGBClient class
        self.async_client_patcher = patch("signalrgb.client.AsyncSignalRGBClient")
        self.mock_async_client_class = self.async_client_patcher.start()

        # Create a mock instance that will be returned by the AsyncSignalRGBClient constructor
        self.mock_async_client = Mock()
        self.mock_async_client_class.return_value = self.mock_async_client

        # Create the client under test
        self.client = SignalRGBClient("testhost", 12345)

        # Verify the AsyncSignalRGBClient was created with the right params
        self.mock_async_client_class.assert_called_once_with("testhost", 12345, 10.0)

    def teardown_method(self, method=None):
        """Clean up after each test."""
        self.async_client_patcher.stop()

    def test_init(self):
        """Test initialization."""
        # Test with default values
        with patch("signalrgb.client.AsyncSignalRGBClient") as mock_async_client:
            client = SignalRGBClient()
            assert client._base_url == f"http://localhost:{DEFAULT_PORT}"
            mock_async_client.assert_called_once_with("localhost", DEFAULT_PORT, 10.0)

        # Test with custom values
        with patch("signalrgb.client.AsyncSignalRGBClient") as mock_async_client:
            client = SignalRGBClient("example.com", 8080, 5.0)
            assert client._base_url == "http://example.com:8080"
            mock_async_client.assert_called_once_with("example.com", 8080, 5.0)

    def test_apply_effect(self):
        """Test applying an effect."""

        # Setup the mock async method
        async def mock_apply_effect(effect_id):
            return None

        self.mock_async_client.apply_effect = mock_apply_effect

        # Call the method under test
        self.client.apply_effect("effect1")

        # We can't verify the call parameters with this approach, but the test passes if no exception is raised

    def test_apply_effect_by_name(self):
        """Test applying an effect by name."""

        # Setup the mock async method
        async def mock_apply_effect_by_name(effect_name):
            return None

        self.mock_async_client.apply_effect_by_name = mock_apply_effect_by_name

        # Call the method under test
        self.client.apply_effect_by_name("Test Effect 1")

        # We can't verify the call parameters with this approach, but the test passes if no exception is raised

    def test_get_effect(self):
        """Test getting an effect."""
        # Setup the mock async method
        effect = Effect(
            id="effect1",
            type="lighting",
            attributes=Attributes(name="Test Effect 1"),
            links=Links(),
        )

        async def mock_get_effect(effect_id):
            assert effect_id == "effect1"  # Verify parameters inside the coroutine
            return effect

        self.mock_async_client.get_effect = mock_get_effect

        # Call the method under test
        result = self.client.get_effect("effect1")

        # Verify the result
        assert result.id == "effect1"
        assert result.attributes.name == "Test Effect 1"

    def test_get_effect_by_name(self):
        """Test getting an effect by name."""
        # Setup the mock async method
        effect = Effect(
            id="effect1",
            type="lighting",
            attributes=Attributes(name="Test Effect 1"),
            links=Links(),
        )

        async def mock_get_effect_by_name(effect_name):
            assert effect_name == "Test Effect 1"  # Verify parameters inside the coroutine
            return effect

        self.mock_async_client.get_effect_by_name = mock_get_effect_by_name

        # Call the method under test
        result = self.client.get_effect_by_name("Test Effect 1")

        # Verify the result
        assert result.id == "effect1"
        assert result.attributes.name == "Test Effect 1"

    def test_get_current_effect(self):
        """Test getting the current effect."""
        # Setup the mock async method
        effect = Effect(
            id="effect1",
            type="lighting",
            attributes=Attributes(name="Test Effect 1"),
            links=Links(),
        )

        async def mock_get_current_effect():
            return effect

        self.mock_async_client.get_current_effect = mock_get_current_effect

        # Call the method under test
        result = self.client.get_current_effect()

        # Verify the result
        assert result.id == "effect1"
        assert result.attributes.name == "Test Effect 1"

    def test_brightness_getter(self):
        """Test getting the brightness."""

        # Setup the mock async method
        async def mock_get_brightness():
            return 75

        self.mock_async_client.get_brightness = mock_get_brightness

        # Call the method under test
        result = self.client.brightness

        # Verify the result
        assert result == 75

    def test_brightness_setter(self):
        """Test setting the brightness."""

        # Setup the mock async method
        async def mock_set_brightness(value):
            assert value == 85  # Verify parameters inside the coroutine

        self.mock_async_client.set_brightness = mock_set_brightness

        # Call the method under test
        self.client.brightness = 85

        # The test passes if no exception is raised

    def test_enabled_getter(self):
        """Test getting the enabled state."""

        # Setup the mock async method
        async def mock_get_enabled():
            return True

        self.mock_async_client.get_enabled = mock_get_enabled

        # Call the method under test
        result = self.client.enabled

        # Verify the result
        assert result is True

    def test_enabled_setter(self):
        """Test setting the enabled state."""

        # Setup the mock async method
        async def mock_set_enabled(value):
            assert value is False  # Verify parameters inside the coroutine

        self.mock_async_client.set_enabled = mock_set_enabled

        # Call the method under test
        self.client.enabled = False

        # The test passes if no exception is raised

    def test_apply_effect_error(self):
        """Test error handling when applying an effect."""
        # Setup the mock async method to raise an error
        error = APIError("API returned non-OK status: error", Error(code="error", title="Error"))

        async def mock_apply_effect(effect_id):
            raise error

        self.mock_async_client.apply_effect = mock_apply_effect

        # Call the method under test and verify the error is raised
        with pytest.raises(APIError) as context:
            self.client.apply_effect("effect1")

        # Verify the error message
        assert "API returned non-OK status" in str(context.value)

    def test_apply_effect_by_name_error(self):
        """Test error handling when applying an effect by name."""
        # Setup the mock async method to raise an error
        error = NotFoundError("Effect 'Nonexistent Effect' not found")

        async def mock_apply_effect_by_name(effect_name):
            raise error

        self.mock_async_client.apply_effect_by_name = mock_apply_effect_by_name

        # Call the method under test and verify the error is raised
        with pytest.raises(NotFoundError) as context:
            self.client.apply_effect_by_name("Nonexistent Effect")

        # Verify the error message
        assert "not found" in str(context.value)

    def test_get_effect_presets(self):
        """Test getting effect presets."""
        # Setup the mock async method
        presets = [
            EffectPreset(id="preset1", type="preset"),
            EffectPreset(id="preset2", type="preset"),
        ]

        async def mock_get_effect_presets(effect_id):
            assert effect_id == "effect1"  # Verify parameters inside the coroutine
            return presets

        self.mock_async_client.get_effect_presets = mock_get_effect_presets

        # Call the method under test
        result = self.client.get_effect_presets("effect1")

        # Verify the result
        assert len(result) == 2
        assert result[0].id == "preset1"
        assert result[1].id == "preset2"

    def test_apply_effect_preset(self):
        """Test applying an effect preset."""

        # Setup the mock async method
        async def mock_apply_effect_preset(effect_id, preset_id):
            assert effect_id == "effect1"  # Verify parameters inside the coroutine
            assert preset_id == "preset1"

        self.mock_async_client.apply_effect_preset = mock_apply_effect_preset

        # Call the method under test
        self.client.apply_effect_preset("effect1", "preset1")

        # The test passes if no exception is raised

    def test_get_layouts(self):
        """Test getting layouts."""
        # Setup the mock async method
        layouts = [
            Layout(id="layout1", type="layout"),
            Layout(id="layout2", type="layout"),
        ]

        async def mock_get_layouts():
            return layouts

        self.mock_async_client.get_layouts = mock_get_layouts

        # Call the method under test
        result = self.client.get_layouts()

        # Verify the result
        assert len(result) == 2
        assert result[0].id == "layout1"
        assert result[1].id == "layout2"

    def test_get_current_layout(self):
        """Test getting the current layout."""
        # Setup the mock async method
        layout = Layout(id="layout1", type="layout")

        async def mock_get_current_layout():
            return layout

        self.mock_async_client.get_current_layout = mock_get_current_layout

        # Call the method under test
        result = self.client.current_layout

        # Verify the result
        assert result.id == "layout1"

    def test_set_current_layout(self):
        """Test setting the current layout."""

        # Setup the mock async method
        async def mock_set_current_layout(layout_id):
            assert layout_id == "layout1"  # Verify parameters inside the coroutine

        self.mock_async_client.set_current_layout = mock_set_current_layout

        # Call the method under test
        self.client.current_layout = "layout1"

        # The test passes if no exception is raised

    def test_get_next_effect(self):
        """Test getting the next effect."""
        # Setup the mock async method
        effect = Effect(
            id="effect2",
            type="lighting",
            attributes=Attributes(name="Test Effect 2"),
            links=Links(),
        )

        async def mock_get_next_effect():
            return effect

        self.mock_async_client.get_next_effect = mock_get_next_effect

        # Call the method under test
        result = self.client.get_next_effect()

        # Verify the result
        assert result.id == "effect2"
        assert result.attributes.name == "Test Effect 2"

    def test_apply_next_effect(self):
        """Test applying the next effect."""
        # Setup the mock async method
        effect = Effect(
            id="effect2",
            type="lighting",
            attributes=Attributes(name="Test Effect 2"),
            links=Links(),
        )

        async def mock_apply_next_effect():
            return effect

        self.mock_async_client.apply_next_effect = mock_apply_next_effect

        # Call the method under test
        result = self.client.apply_next_effect()

        # Verify the result
        assert result.id == "effect2"
        assert result.attributes.name == "Test Effect 2"

    def test_get_previous_effect(self):
        """Test getting the previous effect."""
        # Setup the mock async method
        effect = Effect(
            id="effect1",
            type="lighting",
            attributes=Attributes(name="Test Effect 1"),
            links=Links(),
        )

        async def mock_get_previous_effect():
            return effect

        self.mock_async_client.get_previous_effect = mock_get_previous_effect

        # Call the method under test
        result = self.client.get_previous_effect()

        # Verify the result
        assert result.id == "effect1"
        assert result.attributes.name == "Test Effect 1"

    def test_apply_previous_effect(self):
        """Test applying the previous effect."""
        # Setup the mock async method
        effect = Effect(
            id="effect1",
            type="lighting",
            attributes=Attributes(name="Test Effect 1"),
            links=Links(),
        )

        async def mock_apply_previous_effect():
            return effect

        self.mock_async_client.apply_previous_effect = mock_apply_previous_effect

        # Call the method under test
        result = self.client.apply_previous_effect()

        # Verify the result
        assert result.id == "effect1"
        assert result.attributes.name == "Test Effect 1"

    def test_apply_random_effect(self):
        """Test applying a random effect."""
        # Setup the mock async method
        effect = Effect(
            id="random_effect",
            type="lighting",
            attributes=Attributes(name="Random Effect"),
            links=Links(),
        )

        async def mock_apply_random_effect():
            return effect

        self.mock_async_client.apply_random_effect = mock_apply_random_effect

        # Call the method under test
        result = self.client.apply_random_effect()

        # Verify the result
        assert result.id == "random_effect"
        assert result.attributes.name == "Random Effect"

    def test_refresh_effects(self):
        """Test refreshing effects."""

        # Setup the mock async method
        async def mock_refresh_effects():
            return None

        self.mock_async_client.refresh_effects = mock_refresh_effects

        # Call the method under test
        self.client.refresh_effects()

        # The test passes if no exception is raised


if __name__ == "__main__":
    unittest.main()
