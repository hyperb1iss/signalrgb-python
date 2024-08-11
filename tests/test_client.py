import unittest
from unittest.mock import Mock, patch

from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import Timeout

from signalrgb.client import (
    APIError,
    ConnectionError,
    SignalRGBClient,
)
from signalrgb.model import SignalRGBResponse



class TestSignalRGBClient(unittest.TestCase):
    def setUp(self):
        self.client = SignalRGBClient("testhost", 12345)

    @patch("requests.Session.request")
    def test_get_effects(self, mock_request):
        mock_response = Mock()
        mock_response.json.return_value = {
            "api_version": "1.0",
            "id": 1,
            "method": "GET",
            "status": "ok",
            "data": {
                "items": [
                    {
                        "id": "effect1",
                        "type": "lighting",
                        "attributes": {"name": "Effect 1"},
                        "links": {},
                    },
                    {
                        "id": "effect2",
                        "type": "lighting",
                        "attributes": {"name": "Effect 2"},
                        "links": {},
                    },
                ]
            },
        }
        mock_request.return_value = mock_response

        effects = self.client.get_effects()
        self.assertEqual(len(effects), 2)
        self.assertEqual(effects[0].id, "effect1")
        self.assertEqual(effects[1].id, "effect2")

    @patch("requests.Session.request")
    def test_get_effect(self, mock_request):
        mock_response = Mock()
        mock_response.json.return_value = {
            "api_version": "1.0",
            "id": 1,
            "method": "GET",
            "status": "ok",
            "data": {
                "id": "effect1",
                "type": "lighting",
                "attributes": {"name": "Effect 1"},
                "links": {},
            },
        }
        mock_request.return_value = mock_response

        effect = self.client.get_effect("effect1")
        self.assertEqual(effect.id, "effect1")
        self.assertEqual(effect.attributes.name, "Effect 1")

    @patch("requests.Session.request")
    def test_get_effect_by_name(self, mock_request):
        mock_response_get_effects = Mock()
        mock_response_get_effects.json.return_value = {
            "api_version": "1.0",
            "id": 1,
            "method": "GET",
            "status": "ok",
            "data": {
                "items": [
                    {
                        "id": "effect1",
                        "type": "lighting",
                        "attributes": {"name": "Test Effect 1"},
                        "links": {},
                    }
                ]
            },
        }

        mock_response_get_effect = Mock()
        mock_response_get_effect.json.return_value = {
            "api_version": "1.0",
            "id": 2,
            "method": "GET",
            "status": "ok",
            "data": {
                "id": "effect1",
                "type": "lighting",
                "attributes": {"name": "Test Effect 1"},
                "links": {},
            },
        }

        mock_request.side_effect = [
            mock_response_get_effects,
            mock_response_get_effect,
        ]

        effect = self.client.get_effect_by_name("Test Effect 1")
        self.assertEqual(effect.id, "effect1")
        self.assertEqual(effect.attributes.name, "Test Effect 1")

    @patch("requests.Session.request")
    def test_get_current_effect(self, mock_request):
        mock_response_current_state = Mock()
        mock_response_current_state.json.return_value = {
            "api_version": "1.0",
            "id": 1,
            "method": "GET",
            "status": "ok",
            "data": {
                "attributes": {
                    "name": "Current Effect",
                    "enabled": True,
                    "global_brightness": 50,
                },
                "id": "current_state",
                "links": {},
                "type": "current_state",
            },
        }

        mock_response_get_effect = Mock()
        mock_response_get_effect.json.return_value = {
            "api_version": "1.0",
            "id": 2,
            "method": "GET",
            "status": "ok",
            "data": {
                "id": "current_state",
                "type": "lighting",
                "attributes": {"name": "Current Effect"},
                "links": {},
            },
        }

        mock_request.side_effect = [
            mock_response_current_state,
            mock_response_get_effect,
        ]

        effect = self.client.get_current_effect()
        self.assertEqual(effect.id, "current_state")
        self.assertEqual(effect.attributes.name, "Current Effect")

    @patch("requests.Session.request")
    def test_apply_effect(self, mock_request):
        mock_response = Mock()
        mock_response.json.return_value = {
            "api_version": "1.0",
            "id": 1,
            "method": "POST",
            "status": "ok",
        }
        mock_request.return_value = mock_response

        self.client.apply_effect("effect1")
        mock_request.assert_called_with(
            "POST",
            "http://testhost:12345/api/v1/lighting/effects/effect1/apply",
            timeout=10.0,
        )

    @patch("requests.Session.request")
    def test_apply_effect_by_name(self, mock_request):
        # Mock get_effects
        mock_response_get_effects = Mock()
        mock_response_get_effects.json.return_value = {
            "api_version": "1.0",
            "id": 1,
            "method": "GET",
            "status": "ok",
            "data": {
                "items": [
                    {
                        "id": "effect1",
                        "type": "lighting",
                        "attributes": {"name": "Test Effect 1"},
                        "links": {"apply": "/api/v1/effects/effect1/apply"},
                    }
                ]
            },
        }

        # Mock get_effect
        mock_response_get_effect = Mock()
        mock_response_get_effect.json.return_value = {
            "api_version": "1.0",
            "id": 2,
            "method": "GET",
            "status": "ok",
            "data": {
                "id": "effect1",
                "type": "lighting",
                "attributes": {"name": "Test Effect 1"},
                "links": {"apply": "/api/v1/effects/effect1/apply"},
            },
        }

        # Mock apply effect
        mock_response_apply = Mock()
        mock_response_apply.json.return_value = {
            "api_version": "1.0",
            "id": 3,
            "method": "POST",
            "status": "ok",
        }

        mock_request.side_effect = [
            mock_response_get_effects,
            mock_response_get_effect,
            mock_response_apply,
        ]

        self.client.apply_effect_by_name("Test Effect 1")

        self.assertEqual(mock_request.call_count, 3)
        mock_request.assert_any_call(
            "GET", "http://testhost:12345/api/v1/lighting/effects", timeout=10.0
        )
        mock_request.assert_any_call(
            "GET", "http://testhost:12345/api/v1/lighting/effects/effect1", timeout=10.0
        )
        mock_request.assert_any_call(
            "POST", "http://testhost:12345/api/v1/effects/effect1/apply", timeout=10.0
        )

    @patch("requests.Session.request")
    def test_connection_error(self, mock_request):
        mock_request.side_effect = RequestsConnectionError("Connection failed")

        with self.assertRaises(ConnectionError) as context:
            self.client.get_effects()

        self.assertIn("Failed to connect to SignalRGB API", str(context.exception))

    @patch("requests.Session.request")
    def test_generic_request_exception(self, mock_request):
        mock_request.side_effect = Exception("Unexpected error")

        with self.assertRaises(APIError) as context:
            self.client.get_effects()

        self.assertIn("Failed to retrieve effects", str(context.exception))

    @patch("signalrgb.client.SignalRGBClient._request")
    def test_refresh_effects(self, mock_request):
        # Set up mock responses
        mock_response1 = {
            "api_version": "1.0",
            "id": 1,
            "method": "GET",
            "status": "ok",
            "data": {
                "items": [
                    {
                        "id": "effect1",
                        "type": "lighting",
                        "attributes": {"name": "Effect 1"},
                        "links": {},
                    },
                    {
                        "id": "effect2",
                        "type": "lighting",
                        "attributes": {"name": "Effect 2"},
                        "links": {},
                    },
                ]
            },
        }
        mock_response2 = {
            "api_version": "1.0",
            "id": 2,
            "method": "GET",
            "status": "ok",
            "data": {
                "items": [
                    {
                        "id": "effect3",
                        "type": "lighting",
                        "attributes": {"name": "Effect 3"},
                        "links": {},
                    },
                    {
                        "id": "effect4",
                        "type": "lighting",
                        "attributes": {"name": "Effect 4"},
                        "links": {},
                    },
                ]
            },
        }

        mock_request.side_effect = [mock_response1, mock_response2]

        # First call to get_effects
        effects1 = self.client.get_effects()
        self.assertEqual(len(effects1), 2)
        self.assertEqual(effects1[0].id, "effect1")
        self.assertEqual(effects1[1].id, "effect2")

        # Second call to get_effects (should use cached result)
        effects2 = self.client.get_effects()
        self.assertEqual(effects1, effects2)

        # Verify that _request was only called once
        self.assertEqual(mock_request.call_count, 1)

        # Refresh effects
        self.client.refresh_effects()

        # Call get_effects again (should fetch new data)
        effects3 = self.client.get_effects()
        self.assertEqual(len(effects3), 2)
        self.assertEqual(effects3[0].id, "effect3")
        self.assertEqual(effects3[1].id, "effect4")

        # Verify that _request was called twice in total
        self.assertEqual(mock_request.call_count, 2)

    @patch("requests.Session.request")
    def test_timeout_error(self, mock_request):
        mock_request.side_effect = Timeout("Request timed out")

        with self.assertRaises(ConnectionError) as context:
            self.client.get_effects()

        self.assertIn("Request timed out", str(context.exception))

    @patch("requests.Session.request")
    def test_brightness(self, mock_request):
        mock_response = Mock()
        mock_response.json.return_value = {
            "api_version": "1.0",
            "id": 1,
            "method": "PATCH",
            "status": "ok",
        }
        mock_request.return_value = mock_response

        self.client.brightness = 50
        mock_request.assert_called_with(
            "PATCH",
            "http://testhost:12345/api/v1/lighting/global_brightness",
            json={"global_brightness": 50},
            timeout=10.0,
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
        self.assertEqual(brightness, 50)

    @patch("requests.Session.request")
    def test_enabled(self, mock_request):
        mock_response = Mock()
        mock_response.json.return_value = {
            "api_version": "1.0",
            "id": 1,
            "method": "PATCH",
            "status": "ok",
        }
        mock_request.return_value = mock_response

        self.client.enabled = True
        mock_request.assert_called_with(
            "PATCH",
            "http://testhost:12345/api/v1/lighting/enabled",
            json={"enabled": True},
            timeout=10.0,
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
        self.assertTrue(enabled)

    @patch("requests.Session.request")
    def test_ensure_response_ok(self, mock_request):
        mock_response = Mock()
        mock_response.json.return_value = {
            "api_version": "1.0",
            "id": 1,
            "method": "GET",
            "status": "ok",
        }
        mock_request.return_value = mock_response

        response_data = self.client._request("GET", "/api/v1/lighting/effects")
        response = SignalRGBResponse.from_dict(response_data)
        self.client._ensure_response_ok(response)

        mock_response.json.return_value = {
            "api_version": "1.0",
            "id": 1,
            "method": "GET",
            "status": "error",
            "errors": [{"code": "404", "title": "Not Found"}],
        }

        with self.assertRaises(APIError) as context:
            response_data = self.client._request("GET", "/api/v1/lighting/effects")
            response = SignalRGBResponse.from_dict(response_data)
            self.client._ensure_response_ok(response)

        self.assertIn("API returned non-OK status", str(context.exception))


if __name__ == "__main__":
    unittest.main()
