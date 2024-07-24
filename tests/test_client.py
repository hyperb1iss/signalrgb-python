import unittest
from unittest.mock import Mock, patch

from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import Timeout

from signalrgb.client import (
    APIError,
    ConnectionError,
    SignalRGBClient,
)


class TestSignalRGBClient(unittest.TestCase):
    def setUp(self):
        self.client = SignalRGBClient("testhost", 12345)

    # ... (keep other test methods unchanged)

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


if __name__ == "__main__":
    unittest.main()