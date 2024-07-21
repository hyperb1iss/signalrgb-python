import unittest
from unittest.mock import patch, Mock
from requests.exceptions import ConnectionError as RequestsConnectionError, HTTPError
from signalrgb.client import (
    SignalRGBClient,
    APIError,
    EffectNotFoundError,
)


class TestSignalRGBClient(unittest.TestCase):
    def setUp(self):
        self.client = SignalRGBClient("testhost", 12345)

    @patch("requests.Session.request")
    def test_get_effects(self, mock_request):
        # Mock the API response
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
                        "attributes": {
                            "name": "Test Effect 1",
                            "publisher": "Test Publisher",
                        },
                        "links": {},
                    },
                    {
                        "id": "effect2",
                        "type": "lighting",
                        "attributes": {
                            "name": "Test Effect 2",
                            "publisher": "Test Publisher",
                        },
                        "links": {},
                    },
                ]
            },
        }
        mock_request.return_value = mock_response

        effects = self.client.get_effects()

        self.assertEqual(len(effects), 2)
        self.assertEqual(effects[0].id, "effect1")
        self.assertEqual(effects[0].attributes.name, "Test Effect 1")
        self.assertEqual(effects[1].id, "effect2")
        self.assertEqual(effects[1].attributes.name, "Test Effect 2")

    @patch("requests.Session.request")
    def test_get_effect(self, mock_request):
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "api_version": "1.0",
            "id": 1,
            "method": "GET",
            "status": "ok",
            "data": {
                "id": "effect1",
                "type": "lighting",
                "attributes": {
                    "name": "Test Effect 1",
                    "publisher": "Test Publisher",
                    "description": "A test effect",
                },
                "links": {
                    "self": "/api/v1/effects/effect1",
                    "apply": "/api/v1/effects/effect1/apply",
                },
            },
        }
        mock_request.return_value = mock_response

        effect = self.client.get_effect("effect1")

        self.assertEqual(effect.id, "effect1")
        self.assertEqual(effect.attributes.name, "Test Effect 1")
        self.assertEqual(effect.attributes.description, "A test effect")
        self.assertEqual(effect.links.self, "/api/v1/effects/effect1")
        self.assertEqual(effect.links.apply, "/api/v1/effects/effect1/apply")

    @patch("requests.Session.request")
    def test_apply_effect(self, mock_request):
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "api_version": "1.0",
            "id": 1,
            "method": "POST",
            "status": "ok",
        }
        mock_request.return_value = mock_response

        # This should not raise an exception
        self.client.apply_effect("effect1")

        # Verify that the request was made with the correct method and URL
        mock_request.assert_called_once_with(
            "POST", "http://testhost:12345/api/v1/effects/effect1/apply"
        )

    @patch("requests.Session.request")
    def test_connection_error(self, mock_request):
        mock_request.side_effect = RequestsConnectionError("Connection failed")

        with self.assertRaises(APIError) as context:
            self.client.get_effects()

        self.assertIn("Failed to connect to SignalRGB API", str(context.exception))

    @patch("requests.Session.request")
    def test_http_error(self, mock_request):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "errors": [
                {
                    "code": "not_found",
                    "title": "Not Found",
                    "detail": "The requested resource was not found",
                }
            ]
        }
        mock_request.side_effect = HTTPError(response=mock_response)

        with self.assertRaises(EffectNotFoundError) as context:
            self.client.get_effect("non_existent_effect")
            self.assertIn("HTTP error occurred", str(context.exception))
            self.assertEqual(context.exception.error.code, "not_found")

    @patch("requests.Session.request")
    def test_effect_not_found(self, mock_request):
        # Mock the API response for get_effects
        mock_response = Mock()
        mock_response.json.return_value = {
            "api_version": "1.0",
            "id": 1,
            "method": "GET",
            "status": "ok",
            "data": {"items": []},
        }
        mock_request.return_value = mock_response

        with self.assertRaises(EffectNotFoundError) as context:
            self.client.get_effect_by_name("non_existent_effect")

        self.assertIn("Effect 'non_existent_effect' not found", str(context.exception))

    @patch("requests.Session.request")
    def test_api_error(self, mock_request):
        # Mock an error response
        mock_response = Mock()
        mock_response.json.return_value = {
            "api_version": "1.0",
            "id": 1,
            "method": "GET",
            "status": "error",
            "errors": [
                {
                    "code": "internal_error",
                    "title": "Internal Server Error",
                    "detail": "An unexpected error occurred",
                }
            ],
        }
        mock_request.return_value = mock_response

        with self.assertRaises(APIError) as context:
            self.client.get_effects()

        self.assertIn("API returned non-OK status: error", str(context.exception))
        self.assertEqual(context.exception.error.code, "internal_error")


if __name__ == "__main__":
    unittest.main()
