"""Tests for GeekMagic payload rendering."""

import json
import unittest

from custom_components.geekmagic.const import MAX_PAYLOAD_LENGTH
from custom_components.geekmagic.renderer import render_payload


class FakeState:
    def __init__(self, state, attributes=None):
        self.state = state
        self.attributes = attributes or {}


class FakeStates:
    def __init__(self, states):
        self._states = states

    def get(self, entity_id):
        return self._states.get(entity_id)


class FakeHass:
    def __init__(self, states):
        self.states = FakeStates(states)


class RenderPayloadTests(unittest.TestCase):
    def test_formats_units_binary_states_and_theme(self):
        hass = FakeHass(
            {
                "sensor.living_room": FakeState(
                    "21.5", {"friendly_name": "Obývací pokoj", "unit_of_measurement": "°C"}
                ),
                "binary_sensor.door": FakeState(
                    "on", {"friendly_name": "Vchodové dveře"}
                ),
            }
        )

        payload = json.loads(
            render_payload(
                hass,
                {
                    "title": "Domov",
                    "sources": ["sensor.living_room", "binary_sensor.door"],
                    "layout": "hero",
                    "theme": "ocean",
                },
            )
        )

        self.assertEqual(payload["layout"], "hero")
        self.assertEqual(payload["theme"], "ocean")
        self.assertEqual(payload["items"][0]["value"], "21.5 °C")
        self.assertEqual(payload["items"][1]["value"], "Zapnuto")

    def test_limits_item_count_and_payload_size(self):
        hass = FakeHass(
            {
                f"sensor.item_{index}": FakeState(
                    "温度" * 100,
                    {"friendly_name": "室内温度" * 30, "unit_of_measurement": "度"},
                )
                for index in range(6)
            }
        )

        encoded = render_payload(
            hass,
            {
                "title": "家" * 100,
                "sources": [f"sensor.item_{index}" for index in range(6)],
                "layout": "invalid",
                "theme": "invalid",
            },
        )
        payload = json.loads(encoded)

        self.assertEqual(len(payload["items"]), 4)
        self.assertEqual(payload["layout"], "list")
        self.assertEqual(payload["theme"], "midnight")
        self.assertLessEqual(len(encoded.encode("utf-8")), MAX_PAYLOAD_LENGTH)

    def test_missing_entity_has_readable_fallback(self):
        payload = json.loads(
            render_payload(FakeHass({}), {"sources": ["sensor.missing"]})
        )

        self.assertEqual(payload["items"][0]["value"], "Nedostupné")

    def test_payload_with_czech_characters_fits_utf8_byte_limit(self):
        hass = FakeHass(
            {
                "sensor.time": FakeState(
                    "2026-10-02 15:37:47",
                    {"friendly_name": "Master System Time"},
                ),
                "sensor.outdoor": FakeState(
                    "17.5",
                    {
                        "friendly_name": "Meteostanice Outdoor Temperature",
                        "unit_of_measurement": "°C",
                    },
                ),
                "sensor.power": FakeState(
                    "352",
                    {
                        "friendly_name": "GoodWe MPPT1 Power",
                        "unit_of_measurement": "W",
                    },
                ),
                "sensor.battery": FakeState(
                    "100",
                    {
                        "friendly_name": "GoodWe Battery State of Charge",
                        "unit_of_measurement": "%",
                    },
                ),
            }
        )

        encoded = render_payload(
            hass,
            {
                "title": "GeekMagic",
                "layout": "hero",
                "theme": "midnight",
                "sources": [
                    "sensor.time",
                    "sensor.outdoor",
                    "sensor.power",
                    "sensor.battery",
                ],
            },
        )

        self.assertLessEqual(len(encoded.encode("utf-8")), MAX_PAYLOAD_LENGTH)
        self.assertEqual(len(json.loads(encoded)["items"]), 4)


if __name__ == "__main__":
    unittest.main()
