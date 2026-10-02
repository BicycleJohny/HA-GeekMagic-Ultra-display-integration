"""Build the compact display payload sent to the ESPHome text entity."""

from __future__ import annotations

import json
from typing import Any

from .const import (
    CONF_LAYOUT,
    CONF_SOURCES,
    CONF_THEME,
    CONF_TITLE,
    LAYOUTS,
    MAX_ITEMS,
    MAX_PAYLOAD_BYTES,
    THEMES,
)

_DEFAULT_TITLE = "GeekMagic"
_UNAVAILABLE = "Nedostupné"


def _truncate(value: Any, length: int) -> str:
    text = str(value).replace("\r", " ").replace("\n", " ").strip()
    if len(text) > length:
        return f"{text[: length - 1]}…"
    return text


def _state_text(state: Any) -> str:
    value = str(state.state)
    if value in ("unknown", "unavailable", "None"):
        return _UNAVAILABLE
    if value == "on":
        return "Zapnuto"
    if value == "off":
        return "Vypnuto"

    unit = state.attributes.get("unit_of_measurement")
    if unit and value not in ("unknown", "unavailable"):
        return f"{value} {unit}"
    return value


def render_payload(hass: Any, options: dict[str, Any]) -> str:
    """Render configured HA entities as a bounded JSON payload."""
    items: list[dict[str, str]] = []
    for entity_id in options.get(CONF_SOURCES, [])[:MAX_ITEMS]:
        state = hass.states.get(entity_id)
        if state is None:
            label = entity_id.split(".", 1)[-1].replace("_", " ")
            value = _UNAVAILABLE
        else:
            label = state.attributes.get("friendly_name", entity_id)
            value = _state_text(state)
        items.append(
            {
                "label": _truncate(label, 22),
                "value": _truncate(value, 32),
            }
        )

    payload: dict[str, Any] = {
        "version": 1,
        "title": _truncate(options.get(CONF_TITLE) or _DEFAULT_TITLE, 28),
        "layout": options.get(CONF_LAYOUT)
        if options.get(CONF_LAYOUT) in LAYOUTS
        else "list",
        "theme": options.get(CONF_THEME)
        if options.get(CONF_THEME) in THEMES
        else "midnight",
        "items": items,
    }

    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    while len(encoded.encode("utf-8")) > MAX_PAYLOAD_BYTES:
        strings = [
            (len(value), item, key)
            for item in items
            for key, value in item.items()
            if len(value) > 8
        ]
        if not strings:
            break
        _, item, key = max(strings, key=lambda entry: entry[0])
        item[key] = _truncate(item[key], len(item[key]) - 4)
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    return encoded
