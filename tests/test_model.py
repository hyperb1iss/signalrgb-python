import json
import unittest
from typing import Dict, Any

from signalrgb.model import (
    Effect,
    EffectDetailsResponse,
    EffectList,
    EffectListResponse,
    Attributes,
    Links,
    Error,
    SignalRGBResponse,
)


class TestModel(unittest.TestCase):
    def load_json_data(self, filename: str) -> Dict[str, Any]:
        with open(f"tests/data/{filename}") as file:
            return json.load(file)

    def test_effect_deserialization(self):
        data = self.load_json_data("effect.json")
        response = EffectDetailsResponse.model_validate(data)
        self.assertEqual(response.status, "ok")
        self.assertIsInstance(response.data, Effect)

        effect = response.data
        self.assertIsInstance(effect.attributes, Attributes)
        self.assertIsInstance(effect.links, Links)

        # Test Attributes
        attrs = effect.attributes
        self.assertIsInstance(attrs.name, str)
        self.assertIsInstance(attrs.developer_effect, bool)
        self.assertIsInstance(attrs.uses_audio, bool)
        self.assertIsInstance(attrs.uses_input, bool)
        self.assertIsInstance(attrs.uses_meters, bool)
        self.assertIsInstance(attrs.uses_video, bool)
        self.assertIsInstance(attrs.parameters, dict)

        # Test Links
        self.assertIsInstance(effect.links.apply, str)
        self.assertIsInstance(effect.links.self, str)

        # Test single effect
        self.assertIsInstance(effect.id, str)
        self.assertIsInstance(effect.type, str)

    def test_effect_list_deserialization(self):
        data = self.load_json_data("effect_list.json")
        response = EffectListResponse.model_validate(data)
        self.assertEqual(response.status, "ok")
        self.assertIsInstance(response.data, EffectList)

        effects = response.data
        self.assertIsInstance(effects.items, list)
        for effect in effects.items:
            self.assertIsInstance(effect, Effect)
            self.assertIsInstance(effect.id, str)
            self.assertIsInstance(effect.type, str)
            self.assertIsInstance(effect.attributes, Attributes)
            self.assertIsInstance(effect.links, Links)

    def test_effect_error_deserialization(self):
        data = self.load_json_data("error.json")
        response = EffectDetailsResponse.model_validate(data)
        self.assertEqual(response.status, "error")
        self.assertIsInstance(response.errors, list)
        self.assertGreater(len(response.errors), 0)

        error = response.errors[0]
        self.assertIsInstance(error, Error)
        self.assertEqual(error.code, "404")
        self.assertEqual(error.title, "Not Found")
        self.assertIsInstance(error.detail, str)

    def test_attributes_model(self):
        attrs_data = {
            "name": "Test Effect",
            "description": "A test effect",
            "developer_effect": True,
            "image": "http://example.com/image.png",
            "parameters": {"param1": "value1"},
            "publisher": "Test Publisher",
            "uses_audio": True,
            "uses_input": False,
            "uses_meters": True,
            "uses_video": False,
        }
        attrs = Attributes.model_validate(attrs_data)
        for field, value in attrs_data.items():
            self.assertEqual(getattr(attrs, field), value)

    def test_links_model(self):
        links_data = {
            "apply": "http://api.example.com/apply",
            "self": "http://api.example.com/effect/1",
        }
        links = Links.model_validate(links_data)
        self.assertEqual(links.apply, links_data["apply"])
        self.assertEqual(links.self, links_data["self"])

    def test_signal_rgb_response(self):
        response_data = {
            "api_version": "1.0",
            "id": 12345,
            "method": "GET",
            "params": {"effect_id": "test_effect"},
            "status": "ok",
            "errors": [],
        }
        response = SignalRGBResponse.model_validate(response_data)
        self.assertEqual(response.api_version, "1.0")
        self.assertEqual(response.id, 12345)
        self.assertEqual(response.method, "GET")
        self.assertEqual(response.params, {"effect_id": "test_effect"})
        self.assertEqual(response.status, "ok")
        self.assertEqual(response.errors, [])

    def test_error_model(self):
        error_data = {
            "code": "500",
            "title": "Internal Server Error",
            "detail": "An unexpected error occurred",
        }
        error = Error.model_validate(error_data)
        self.assertEqual(error.code, "500")
        self.assertEqual(error.title, "Internal Server Error")
        self.assertEqual(error.detail, "An unexpected error occurred")


if __name__ == "__main__":
    unittest.main()
