import unittest
from unittest.mock import patch, Mock
from signalrgb.client import SignalRGBClient, SignalRGBException
from signalrgb.model import Effect, Attributes, Links, EffectListResponse, EffectDetailsResponse, SignalRGBResponse, Error

class TestSignalRGBClient(unittest.TestCase):

    def setUp(self):
        self.client = SignalRGBClient("testhost", 12345)

    @patch('requests.Session.request')
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
                            "publisher": "Test Publisher"
                        },
                        "links": {}
                    },
                    {
                        "id": "effect2",
                        "type": "lighting",
                        "attributes": {
                            "name": "Test Effect 2",
                            "publisher": "Test Publisher"
                        },
                        "links": {}
                    }
                ]
            }
        }
        mock_request.return_value = mock_response

        effects = self.client.get_effects()

        self.assertEqual(len(effects), 2)
        self.assertEqual(effects[0].id, "effect1")
        self.assertEqual(effects[0].attributes.name, "Test Effect 1")
        self.assertEqual(effects[1].id, "effect2")
        self.assertEqual(effects[1].attributes.name, "Test Effect 2")

    @patch('requests.Session.request')
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
                    "description": "A test effect"
                },
                "links": {
                    "self": "/api/v1/effects/effect1",
                    "apply": "/api/v1/effects/effect1/apply"
                }
            }
        }
        mock_request.return_value = mock_response

        effect = self.client.get_effect("effect1")

        self.assertEqual(effect.id, "effect1")
        self.assertEqual(effect.attributes.name, "Test Effect 1")
        self.assertEqual(effect.attributes.description, "A test effect")
        self.assertEqual(effect.links.self, "/api/v1/effects/effect1")
        self.assertEqual(effect.links.apply, "/api/v1/effects/effect1/apply")

    @patch('requests.Session.request')
    def test_apply_effect(self, mock_request):
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "api_version": "1.0",
            "id": 1,
            "method": "POST",
            "status": "ok"
        }
        mock_request.return_value = mock_response

        # This should not raise an exception
        self.client.apply_effect("effect1")

        # Verify that the request was made with the correct method and URL
        mock_request.assert_called_once_with("POST", "http://testhost:12345/api/v1/effects/effect1/apply")

    @patch('requests.Session.request')
    def test_error_handling(self, mock_request):
        # Mock an error response
        mock_response = Mock()
        mock_response.json.return_value = {
            "api_version": "1.0",
            "id": 1,
            "method": "GET",
            "status": "error",
            "errors": [
                {
                    "code": "not_found",
                    "title": "Effect not found",
                    "detail": "The requested effect does not exist"
                }
            ]
        }
        mock_request.return_value = mock_response

        with self.assertRaises(SignalRGBException) as context:
            self.client.get_effect("non_existent_effect")

        self.assertEqual(str(context.exception), "Effect not found")

if __name__ == '__main__':
    unittest.main()