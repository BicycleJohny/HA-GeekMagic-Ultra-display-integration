"""Constants for the GeekMagic integration."""

from typing import Final

DOMAIN: Final = "geekmagic"

CONF_PAYLOAD_ENTITY: Final = "payload_entity"
CONF_SOURCES: Final = "sources"
CONF_TITLE: Final = "title"
CONF_LAYOUT: Final = "layout"
CONF_THEME: Final = "theme"

LAYOUTS: Final = ("list", "hero", "compact")
THEMES: Final = ("midnight", "ocean", "amber", "light")
MAX_ITEMS: Final = 4
MAX_PAYLOAD_BYTES: Final = 480
