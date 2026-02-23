from __future__ import annotations

import base64
from typing import Any

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import CoverCoordinator, CoverData
from .const import DOMAIN


_PLACEHOLDER_IMAGE = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO7Z8rQAAAAASUVORK5CYII="
)


def _source_name(source_entity_id: str) -> str:
    object_id = source_entity_id.split(".", 1)[-1]
    return object_id.replace("_", " ").title()


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: CoverCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MediaCoverArtImage(coordinator, entry)], update_before_add=False)


class MediaCoverArtImage(CoordinatorEntity[CoverCoordinator], ImageEntity):
    _attr_has_entity_name = True
    _attr_icon = "mdi:disc"

    def __init__(self, coordinator: CoverCoordinator, entry: ConfigEntry) -> None:
        CoordinatorEntity.__init__(self, coordinator)
        ImageEntity.__init__(self)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_cover"
        self._attr_name = f"Cover {_source_name(coordinator.source_entity_id)}"
        self._attr_content_type = "image/jpeg"

    @property
    def image_last_updated(self):
        data: CoverData | None = self.coordinator.data
        return data.last_updated if data else None

    async def async_image(self) -> bytes | None:
        data: CoverData | None = self.coordinator.data
        if not data or not data.image:
            self._attr_content_type = "image/png"
            return _PLACEHOLDER_IMAGE
        self._attr_content_type = data.content_type or "image/jpeg"
        return data.image

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data: CoverData | None = self.coordinator.data
        base = {
            "source_entity_id": self.coordinator.source_entity_id,
        }
        if not data:
            return base

        return {
            **base,
            "track_key": data.track_key,
            "artist": data.artist,
            "title": data.title,
            "album": data.album,
            "provider": data.provider,
            "artwork_url": data.artwork_url,
            "artwork_width": self.coordinator.artwork_width,
            "artwork_height": self.coordinator.artwork_height,
            "artwork_size": self.coordinator.artwork_size,
        }
