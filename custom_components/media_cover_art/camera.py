from __future__ import annotations

from pathlib import Path
from typing import Any

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import CoverCoordinator, CoverData
from .const import DOMAIN

_FALLBACK_SVG = (Path(__file__).parent / "no_cover.svg").read_bytes()


def _source_name(source_entity_id: str) -> str:
    object_id = source_entity_id.split(".", 1)[-1]
    return object_id.replace("_", " ").title()


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: CoverCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MediaCoverArtCamera(coordinator, entry)], update_before_add=False)


class MediaCoverArtCamera(CoordinatorEntity[CoverCoordinator], Camera):
    _attr_has_entity_name = True
    _attr_icon = "mdi:image"

    def __init__(self, coordinator: CoverCoordinator, entry: ConfigEntry) -> None:
        CoordinatorEntity.__init__(self, coordinator)
        try:
            Camera.__init__(self)
        except TypeError:
            # Compatibility guard for potential signature differences across HA versions.
            try:
                Camera.__init__(self, coordinator.hass)
            except TypeError:
                Camera.__init__(self, hass=coordinator.hass)
        self._attr_unique_id = f"{entry.entry_id}_cover_camera"
        self._attr_name = f"Cover {_source_name(coordinator.source_entity_id)}"
        self._attr_is_streaming = False
        self.content_type = "image/svg+xml"

    async def async_camera_image(self, width: int | None = None, height: int | None = None) -> bytes | None:
        data: CoverData | None = self.coordinator.data
        if not data or not data.image:
            self.content_type = "image/svg+xml"
            return _FALLBACK_SVG
        self.content_type = data.content_type or "image/jpeg"
        return data.image

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data: CoverData | None = self.coordinator.data
        return {
            "source_entity_id": self.coordinator.source_entity_id,
            "track_key": data.track_key if data else None,
            "artist": data.artist if data else None,
            "title": data.title if data else None,
            "album": data.album if data else None,
            "provider": data.provider if data else None,
            "artwork_url": data.artwork_url if data else None,
            "artwork_width": self.coordinator.artwork_width,
            "artwork_height": self.coordinator.artwork_height,
            "artwork_size": self.coordinator.artwork_size,
        }
