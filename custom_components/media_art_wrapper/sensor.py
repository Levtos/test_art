from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import CoverCoordinator, CoverData
from .const import DOMAIN
from .helpers import source_name


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: CoverCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MediaCoverArtStatusSensor(coordinator, entry)], update_before_add=False)


class MediaCoverArtStatusSensor(CoordinatorEntity[CoverCoordinator], SensorEntity):
    _attr_has_entity_name = False
    _attr_icon = "mdi:music-circle"

    def __init__(self, coordinator: CoverCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_cover_status"
        self._attr_name = f"{source_name(coordinator.source_entity_id)} Cover Status"

    @property
    def native_value(self) -> str:
        data: CoverData | None = self.coordinator.data
        if not data:
            return "idle"
        if data.image:
            return "ready"
        if data.track_key:
            return "not_found"
        return "idle"

    @property
    def available(self) -> bool:
        # Keep a stable fallback entity available even if media player is temporarily unavailable.
        return True

    @property
    def extra_state_attributes(self) -> dict[str, str | int | None]:
        data: CoverData | None = self.coordinator.data
        source_state = self.coordinator.hass.states.get(self.coordinator.source_entity_id)
        return {
            "source_entity_id": self.coordinator.source_entity_id,
            "source_state": source_state.state if source_state else None,
            "track_key": data.track_key if data else None,
            "artist": data.artist if data else None,
            "title": data.title if data else None,
            "album": data.album if data else None,
            "provider": data.provider if data else None,
            "artwork_url": data.artwork_url if data else None,
            "artwork_width": self.coordinator.artwork_width,
            "artwork_height": self.coordinator.artwork_height,
            "artwork_size": self.coordinator.artwork_size,
            "last_error": self.coordinator.last_error,
        }
