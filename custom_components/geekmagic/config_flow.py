"""Config and options flows for GeekMagic displays."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_LAYOUT,
    CONF_PAYLOAD_ENTITY,
    CONF_SOURCES,
    CONF_THEME,
    CONF_TITLE,
    DOMAIN,
    LAYOUTS,
    MAX_ITEMS,
    THEMES,
)


def _settings_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    """Create the shared display settings form."""
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_TITLE, default=defaults.get(CONF_TITLE, "GeekMagic")
            ): selector.TextSelector(),
            vol.Required(
                CONF_SOURCES, default=defaults.get(CONF_SOURCES, [])
            ): selector.EntitySelector(selector.EntitySelectorConfig(multiple=True)),
            vol.Required(
                CONF_LAYOUT, default=defaults.get(CONF_LAYOUT, "list")
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        {"label": label, "value": value}
                        for label, value in zip(
                            ("Seznam", "Hlavní hodnota", "Kompaktní"),
                            LAYOUTS,
                            strict=True,
                        )
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(
                CONF_THEME, default=defaults.get(CONF_THEME, "midnight")
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        {"label": label, "value": value}
                        for label, value in zip(
                            ("Půlnoční", "Oceán", "Jantar", "Světlé"),
                            THEMES,
                            strict=True,
                        )
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
        }
    )


def _valid_settings(
    user_input: dict[str, Any], payload_entity: str | None = None
) -> str | None:
    """Keep the payload small enough for the ESP8266 text entity."""
    sources = user_input.get(CONF_SOURCES, [])
    if len(sources) > MAX_ITEMS:
        return "too_many_sources"
    if payload_entity is not None and payload_entity in sources:
        return "payload_is_source"
    return None


class GeekMagicConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Set up a GeekMagic display."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Pick the ESPHome text entity and initial display settings."""
        errors: dict[str, str] = {}
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_PAYLOAD_ENTITY])
            self._abort_if_unique_id_configured()
            error = _valid_settings(user_input, user_input[CONF_PAYLOAD_ENTITY])
            if error is None:
                return self.async_create_entry(
                    title=user_input[CONF_TITLE],
                    data={CONF_PAYLOAD_ENTITY: user_input[CONF_PAYLOAD_ENTITY]},
                    options={
                        key: user_input[key]
                        for key in (CONF_TITLE, CONF_SOURCES, CONF_LAYOUT, CONF_THEME)
                    },
                )
            errors["base"] = error

        schema = vol.Schema(
            {
                vol.Required(CONF_PAYLOAD_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="text", integration="esphome"
                    )
                ),
                **_settings_schema().schema,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> GeekMagicOptionsFlow:
        """Return the options flow."""
        return GeekMagicOptionsFlow(config_entry)


class GeekMagicOptionsFlow(config_entries.OptionsFlow):
    """Edit a display's source entities and appearance."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Save display settings."""
        errors: dict[str, str] = {}
        if user_input is not None:
            error = _valid_settings(
                user_input, self._entry.data[CONF_PAYLOAD_ENTITY]
            )
            if error is None:
                return self.async_create_entry(title="", data=user_input)
            errors["base"] = error

        return self.async_show_form(
            step_id="init",
            data_schema=_settings_schema(dict(self._entry.options)),
            errors=errors,
        )
