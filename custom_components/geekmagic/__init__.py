"""Home Assistant integration for GeekMagic ESPHome displays."""

from __future__ import annotations

import logging
from collections.abc import Callable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.event import async_track_state_change_event

from .const import CONF_PAYLOAD_ENTITY, CONF_SOURCES
from .renderer import render_payload

_LOGGER = logging.getLogger(__name__)
GeekMagicConfigEntry = ConfigEntry


async def async_setup_entry(
    hass: HomeAssistant, entry: GeekMagicConfigEntry
) -> bool:
    """Set up a display sender and watch the configured HA entities."""
    sources = tuple(entry.options.get(CONF_SOURCES, []))

    async def async_send_payload() -> None:
        payload_entity = entry.data[CONF_PAYLOAD_ENTITY]
        if hass.states.get(payload_entity) is None:
            _LOGGER.warning(
                "ESPHome payload entity %s is missing; check the device connection",
                payload_entity,
            )
            return

        payload = render_payload(hass, dict(entry.options))
        try:
            await hass.services.async_call(
                "text",
                "set_value",
                {"entity_id": payload_entity, "value": payload},
                blocking=False,
            )
        except HomeAssistantError:
            _LOGGER.exception(
                "Unable to send display data to ESPHome entity %s", payload_entity
            )

    @callback
    def _source_changed(event: Event) -> None:
        if event.data.get("entity_id") == entry.data[CONF_PAYLOAD_ENTITY]:
            return
        hass.async_create_task(async_send_payload())

    async def _on_entry_update(
        hass: HomeAssistant, updated_entry: GeekMagicConfigEntry
    ) -> None:
        await async_reload_entry(hass, updated_entry)

    remove_listener: Callable[[], None] | None = None
    if sources:
        remove_listener = async_track_state_change_event(
            hass, sources, _source_changed
        )

    entry.async_on_unload(
        lambda: remove_listener() if remove_listener is not None else None
    )
    entry.async_on_unload(entry.add_update_listener(_on_entry_update))
    hass.async_create_task(async_send_payload())
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: GeekMagicConfigEntry
) -> bool:
    """Unload the entry."""
    return True


async def async_reload_entry(
    hass: HomeAssistant, entry: GeekMagicConfigEntry
) -> None:
    """Reload when the user changes display settings."""
    await hass.config_entries.async_reload(entry.entry_id)
