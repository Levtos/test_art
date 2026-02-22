from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, State, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    CONF_ARTWORK_SIZE,
    CONF_PROVIDERS,
    CONF_SOURCE_ENTITY_ID,
    DEFAULT_ARTWORK_SIZE,
    DEFAULT_PROVIDERS,
    DOMAIN,
    PLATFORMS,
)
from .cover_resolver import async_resolve_cover
from .models import TrackQuery

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class CoverData:
    source_entity_id: str
    track_key: str | None
    artist: str | None
    title: str | None
    album: str | None
    provider: str | None
    artwork_url: str | None
    content_type: str
    image: bytes | None
    last_updated: datetime | None


def _norm(s: str) -> str:
    return " ".join(s.strip().lower().split())


def _build_track_key(artist: str | None, title: str | None, album: str | None) -> str | None:
    if not artist and not title:
        return None
    parts = [
        _norm(artist) if artist else "",
        _norm(title) if title else "",
        _norm(album) if album else "",
    ]
    return "|".join(parts)


class CoverCoordinator(DataUpdateCoordinator[CoverData]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.source_entity_id: str = entry.data[CONF_SOURCE_ENTITY_ID]
        self.providers: list[str] = []
        self.artwork_size: int = DEFAULT_ARTWORK_SIZE

        self._session = aiohttp_client.async_get_clientsession(hass)
        self._unsub_state_change: Any | None = None
        self._lock = asyncio.Lock()

        self._update_from_entry(entry)

        self._artist: str | None = None
        self._title: str | None = None
        self._album: str | None = None
        self._track_key: str | None = None

        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=f"{DOMAIN}:{self.source_entity_id}",
            update_method=self._async_update_data,
            update_interval=None,  # event-driven
        )

    def _update_from_entry(self, entry: ConfigEntry) -> None:
        providers = entry.options.get(CONF_PROVIDERS, entry.data.get(CONF_PROVIDERS, DEFAULT_PROVIDERS))
        self.providers = list(providers) if isinstance(providers, list) else list(DEFAULT_PROVIDERS)

        artwork_size = entry.options.get(CONF_ARTWORK_SIZE, entry.data.get(CONF_ARTWORK_SIZE, DEFAULT_ARTWORK_SIZE))
        self.artwork_size = int(artwork_size)


    async def async_start(self) -> None:
        """Start listening to media_player state changes and do initial refresh."""
        if self._unsub_state_change is not None:
            return

        self._unsub_state_change = async_track_state_change_event(
            self.hass,
            [self.source_entity_id],
            self._handle_state_change,
        )

        # Initialize from current state (if available)
        state = self.hass.states.get(self.source_entity_id)
        changed = self._set_track_from_state(state)
        # Even if not changed, try one refresh on start in case there's already data
        if changed or state is not None:
            await self.async_request_refresh()

    async def async_stop(self) -> None:
        """Stop listeners."""
        if self._unsub_state_change is not None:
            self._unsub_state_change()
            self._unsub_state_change = None

    @callback
    def _handle_state_change(self, event) -> None:
        new_state: State | None = event.data.get("new_state")
        if new_state is None:
            return

        changed = self._set_track_from_state(new_state)
        if not changed:
            return

        # schedule refresh (callback context)
        self.hass.async_create_task(self.async_request_refresh())

    def _set_track_from_state(self, state: State | None) -> bool:
        if state is None:
            return False

        attrs = state.attributes or {}
        artist = attrs.get("media_artist")
        title = attrs.get("media_title")
        album = attrs.get("media_album_name")

        # Normalize empty strings to None
        artist = artist.strip() if isinstance(artist, str) else None
        title = title.strip() if isinstance(title, str) else None
        album = album.strip() if isinstance(album, str) else None

        new_key = _build_track_key(artist, title, album)

        if new_key == self._track_key:
            return False

        self._artist = artist
        self._title = title
        self._album = album
        self._track_key = new_key
        return True

    async def _async_update_data(self) -> CoverData:
        """Fetch and cache cover data for current track."""
        async with self._lock:
            track_key = self._track_key
            artist = self._artist
            title = self._title
            album = self._album

            if not track_key or (not artist and not title):
                return CoverData(
                    source_entity_id=self.source_entity_id,
                    track_key=None,
                    artist=artist,
                    title=title,
                    album=album,
                    provider=None,
                    artwork_url=None,
                    content_type="image/jpeg",
                    image=None,
                    last_updated=None,
                )

            try:
                query = TrackQuery(
                    artist=artist,
                    title=title,
                    album=album,
                    artwork_size=self.artwork_size,
                )
                resolved = await async_resolve_cover(
                    session=self._session,
                    query=query,
                    providers=self.providers,
                )
            except (asyncio.TimeoutError, HomeAssistantError) as err:
                raise UpdateFailed(str(err)) from err
            except Exception as err:
                raise UpdateFailed(f"Unexpected error: {err}") from err

            if resolved is None:
                return CoverData(
                    source_entity_id=self.source_entity_id,
                    track_key=track_key,
                    artist=artist,
                    title=title,
                    album=album,
                    provider=None,
                    artwork_url=None,
                    content_type="image/jpeg",
                    image=None,
                    last_updated=None,
                )

            return CoverData(
                source_entity_id=self.source_entity_id,
                track_key=track_key,
                artist=artist,
                title=title,
                album=album,
                provider=resolved.provider,
                artwork_url=resolved.artwork_url,
                content_type=resolved.content_type,
                image=resolved.image,
                last_updated=dt_util.utcnow(),
            )


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = CoverCoordinator(hass, entry)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    await coordinator.async_start()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator: CoverCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_stop()
    return unload_ok
