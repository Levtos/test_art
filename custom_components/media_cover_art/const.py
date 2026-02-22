from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "media_cover_art"

PLATFORMS: list[Platform] = [Platform.IMAGE]

CONF_SOURCE_ENTITY_ID = "source_entity_id"
CONF_PROVIDERS = "providers"
CONF_ARTWORK_SIZE = "artwork_size"

PROVIDER_ITUNES = "itunes"

DEFAULT_PROVIDERS: list[str] = [PROVIDER_ITUNES]
DEFAULT_ARTWORK_SIZE = 600
