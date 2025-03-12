import json
from typing import Any, cast
import unittest

from signalrgb.model import (
    Attributes,
    Effect,
    EffectDetailsResponse,
    EffectList,
    EffectListResponse,
    Error,
    Links,
    SignalRGBResponse,
)


class TestModel(unittest.TestCase):
    def load_json_data(self, filename: str) -> dict[str, Any]:
        with open(f"tests/data/{filename}", encoding="utf-8") as file:
            return cast(dict[str, Any], json.load(file))

    def test_effect_deserialization(self):
        data = self.load_json_data("effect.json")
        response = EffectDetailsResponse.from_dict(data)
        assert response.status == "ok"
        assert isinstance(response.data, Effect)

        effect = response.data
        assert isinstance(effect.attributes, Attributes)
        assert isinstance(effect.links, Links)

        # Test Attributes
        attrs = effect.attributes
        assert isinstance(attrs.name, str)
        assert isinstance(attrs.developer_effect, bool)
        assert isinstance(attrs.uses_audio, bool)
        assert isinstance(attrs.uses_input, bool)
        assert isinstance(attrs.uses_meters, bool)
        assert isinstance(attrs.uses_video, bool)
        assert isinstance(attrs.parameters, dict)

        # Test Links
        assert isinstance(effect.links.apply, str)
        assert isinstance(effect.links.self_link, str)

        # Test single effect
        assert isinstance(effect.id, str)
        assert isinstance(effect.type, str)

    def test_effect_list_deserialization(self):
        data = self.load_json_data("effect_list.json")
        response = EffectListResponse.from_dict(data)
        assert response.status == "ok"
        assert isinstance(response.data, EffectList)

        effects = response.data
        assert isinstance(effects.items, list)
        for effect in effects.items:
            assert isinstance(effect, Effect)
            assert isinstance(effect.id, str)
            assert isinstance(effect.type, str)
            assert isinstance(effect.attributes, Attributes)
            assert isinstance(effect.links, Links)

    def test_effect_error_deserialization(self):
        data = self.load_json_data("error.json")
        response = EffectDetailsResponse.from_dict(data)
        assert response.status == "error"
        assert isinstance(response.errors, list)
        assert len(response.errors) > 0

        error = response.errors[0]
        assert isinstance(error, Error)
        assert error.code == "404"
        assert error.title == "Not Found"
        assert isinstance(error.detail, str)

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
        attrs = Attributes.from_dict(attrs_data)
        for field, value in attrs_data.items():
            assert getattr(attrs, field) == value

    def test_links_model(self):
        links_data = {
            "apply": "http://api.example.com/apply",
            "self": "http://api.example.com/effect/1",
        }
        links = Links.from_dict(links_data)
        assert links.apply == links_data["apply"]
        assert links.self_link == links_data["self"]

    def test_signal_rgb_response(self):
        response_data = {
            "api_version": "1.0",
            "id": 12345,
            "method": "GET",
            "params": {"effect_id": "test_effect"},
            "status": "ok",
            "errors": [],
        }
        response = SignalRGBResponse.from_dict(response_data)
        assert response.api_version == "1.0"
        assert response.id == 12345
        assert response.method == "GET"
        assert response.params == {"effect_id": "test_effect"}
        assert response.status == "ok"
        assert response.errors == []

    def test_error_model(self):
        error_data = {
            "code": "500",
            "title": "Internal Server Error",
            "detail": "An unexpected error occurred",
        }
        error = Error.from_dict(error_data)
        assert error.code == "500"
        assert error.title == "Internal Server Error"
        assert error.detail == "An unexpected error occurred"


if __name__ == "__main__":
    unittest.main()
