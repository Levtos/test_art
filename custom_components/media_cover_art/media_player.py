from __future__ import annotations

from typing import Any

from homeassistant.components.media_player import MediaPlayerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import CoverCoordinator, CoverData
from .const import DOMAIN
from .helpers import FALLBACK_IMAGE, source_name


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: CoverCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MediaCoverArtPlayer(coordinator, entry)], update_before_add=False)


class MediaCoverArtPlayer(CoordinatorEntity[CoverCoordinator], MediaPlayerEntity):
    """Media-player wrapper that keeps controls from source player and cover from this integration."""

    _attr_icon = "mdi:speaker"

    def __init__(self, coordinator: CoverCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_cover_player"
        self._attr_name = f"{source_name(coordinator.source_entity_id)} Cover"

    @property
    def source_entity_id(self) -> str:
        return self.coordinator.source_entity_id

    @property
    def source_state(self):
        return self.hass.states.get(self.source_entity_id)

    @property
    def available(self) -> bool:
        return self.source_state is not None

    @property
    def state(self):
        src = self.source_state
        return src.state if src else None

    @property
    def supported_features(self) -> int:
        src = self.source_state
        if not src:
            return 0
        return int(src.attributes.get("supported_features", 0))

    @property
    def media_title(self) -> str | None:
        src = self.source_state
        return src.attributes.get("media_title") if src else None

    @property
    def media_artist(self) -> str | None:
        src = self.source_state
        return src.attributes.get("media_artist") if src else None

    @property
    def media_album_name(self) -> str | None:
        src = self.source_state
        return src.attributes.get("media_album_name") if src else None

    @property
    def media_duration(self) -> int | None:
        src = self.source_state
        return src.attributes.get("media_duration") if src else None

    @property
    def media_position(self) -> int | None:
        src = self.source_state
        return src.attributes.get("media_position") if src else None

    @property
    def media_position_updated_at(self):
        src = self.source_state
        return src.attributes.get("media_position_updated_at") if src else None

    @property
    def volume_level(self) -> float | None:
        src = self.source_state
        return src.attributes.get("volume_level") if src else None

    @property
    def is_volume_muted(self) -> bool | None:
        src = self.source_state
        return src.attributes.get("is_volume_muted") if src else None

    @property
    def source(self) -> str | None:
        src = self.source_state
        return src.attributes.get("source") if src else None

    @property
    def source_list(self) -> list[str] | None:
        src = self.source_state
        return src.attributes.get("source_list") if src else None

    @property
    def sound_mode(self) -> str | None:
        src = self.source_state
        return src.attributes.get("sound_mode") if src else None

    @property
    def sound_mode_list(self) -> list[str] | None:
        src = self.source_state
        return src.attributes.get("sound_mode_list") if src else None

    @property
    def shuffle(self) -> bool | None:
        src = self.source_state
        return src.attributes.get("shuffle") if src else None

    @property
    def repeat(self) -> str | None:
        src = self.source_state
        return src.attributes.get("repeat") if src else None

    @property
    def media_image_hash(self) -> str | None:
        data: CoverData | None = self.coordinator.data
        return data.track_key if data else None

    async def async_get_media_image(self):
        data: CoverData | None = self.coordinator.data
        if not data or not data.image:
            return FALLBACK_IMAGE, "image/png"
        return data.image, data.content_type or "image/jpeg"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data: CoverData | None = self.coordinator.data
        return {
            "source_entity_id": self.source_entity_id,
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

    async def _async_call_source(self, service: str, **service_data: Any) -> None:
        await self.hass.services.async_call(
            "media_player",
            service,
            {"entity_id": self.source_entity_id, **service_data},
            blocking=True,
        )

    async def async_turn_on(self) -> None:
        await self._async_call_source("turn_on")

    async def async_turn_off(self) -> None:
        await self._async_call_source("turn_off")

    async def async_toggle(self) -> None:
        await self._async_call_source("toggle")

    async def async_media_play(self) -> None:
        await self._async_call_source("media_play")

    async def async_media_pause(self) -> None:
        await self._async_call_source("media_pause")

    async def async_media_stop(self) -> None:
        await self._async_call_source("media_stop")

    async def async_media_next_track(self) -> None:
        await self._async_call_source("media_next_track")

    async def async_media_previous_track(self) -> None:
        await self._async_call_source("media_previous_track")

    async def async_set_volume_level(self, volume: float) -> None:
        await self._async_call_source("volume_set", volume_level=volume)

    async def async_volume_up(self) -> None:
        await self._async_call_source("volume_up")

    async def async_volume_down(self) -> None:
        await self._async_call_source("volume_down")

    async def async_mute_volume(self, mute: bool) -> None:
        await self._async_call_source("volume_mute", is_volume_muted=mute)

    async def async_media_seek(self, position: float) -> None:
        await self._async_call_source("media_seek", seek_position=position)

    async def async_play_media(self, media_type: str, media_id: str, **kwargs: Any) -> None:
        await self._async_call_source("play_media", media_content_type=media_type, media_content_id=media_id, **kwargs)

    async def async_select_source(self, source: str) -> None:
        await self._async_call_source("select_source", source=source)

    async def async_select_sound_mode(self, sound_mode: str) -> None:
        await self._async_call_source("select_sound_mode", sound_mode=sound_mode)

    async def async_set_shuffle(self, shuffle: bool) -> None:
        await self._async_call_source("shuffle_set", shuffle=shuffle)

    async def async_set_repeat(self, repeat: str) -> None:
        await self._async_call_source("repeat_set", repeat=repeat)

    async def async_clear_playlist(self) -> None:
        await self._async_call_source("clear_playlist")
