import unittest
import json
from signalrgb.model import (
    Effect,
    EffectDetailsResponse,
    EffectList,
    EffectListResponse,
)


class TestModel(unittest.TestCase):
    def load_json_data(self, filename):
        with open(f"tests/data/{filename}") as file:
            return json.load(file)

    def test_effect_deserialization(self):
        data = self.load_json_data("effect.json")

        response = EffectDetailsResponse.model_validate(data)
        self.assertEqual(response.status, "ok")

        effect = response.data
        assert isinstance(effect, Effect)
        print("effect:", effect)

    def test_effect_list_deserialization(self):
        data = self.load_json_data("effect_list.json")

        response = EffectListResponse.model_validate(data)
        self.assertEqual(response.status, "ok")

        effects = response.data
        assert isinstance(effects, EffectList)
        assert isinstance(effects.items, list)
        for effect in effects.items:
            assert isinstance(effect, Effect)
        print("effects:", effects.items)

    def test_effect_error_deserialization(self):
        data = self.load_json_data("error.json")

        response = EffectDetailsResponse.model_validate(data)
        self.assertEqual(response.status, "error")

        error = response.errors[0]
        self.assertEqual(error.code, "404")
        self.assertEqual(error.title, "Not Found")
        print("error:", error)
