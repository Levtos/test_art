from __future__ import annotations

from typing import Any

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import CoverCoordinator, CoverData
from .const import DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: CoverCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MediaCoverArtImage(coordinator, entry)], update_before_add=False)


class MediaCoverArtImage(CoordinatorEntity[CoverCoordinator], ImageEntity):
    _attr_has_entity_name = True
    _attr_name = "Cover"

    def __init__(self, coordinator: CoverCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_cover"
        # default; can be overwritten by coordinator data
        self._attr_content_type = "image/jpeg"

    @property
    def available(self) -> bool:
        # available when source entity exists; coordinator itself may have no image sometimes
        return self.coordinator.hass.states.get(self.coordinator.source_entity_id) is not None

    @property
    def image_last_updated(self):
        data: CoverData | None = self.coordinator.data
        return data.last_updated if data else None

    async def async_image(self) -> bytes | None:
        data: CoverData | None = self.coordinator.data
        if not data:
            return None
        if data.content_type:
            self._attr_content_type = data.content_type
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
            "artwork_size": self.coordinator.artwork_size,
        }
