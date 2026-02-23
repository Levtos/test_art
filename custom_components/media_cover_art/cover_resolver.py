from __future__ import annotations

import logging
from typing import Iterable

from .const import PROVIDER_ITUNES, PROVIDER_MUSICBRAINZ
from .itunes import async_itunes_resolve
from .models import ResolvedCover, TrackQuery
from .musicbrainz import async_musicbrainz_resolve

_LOGGER = logging.getLogger(__name__)


async def async_resolve_cover(*, session, query: TrackQuery, providers: Iterable[str]) -> ResolvedCover | None:
    """Try providers in order and return first match."""
    provider_list = [p for p in providers if isinstance(p, str)]
    if not provider_list:
        provider_list = [PROVIDER_ITUNES]

    last_err: Exception | None = None

    for provider in provider_list:
        try:
            if provider == PROVIDER_ITUNES:
                resolved = await async_itunes_resolve(session=session, query=query)
                if resolved:
                    return resolved
                continue

            if provider == PROVIDER_MUSICBRAINZ:
                resolved = await async_musicbrainz_resolve(session=session, query=query)
                if resolved:
                    return resolved
                continue

            _LOGGER.debug("Unknown provider '%s' (skipping)", provider)

        except Exception as err:  # noqa: BLE001
            last_err = err
            _LOGGER.debug("Provider '%s' failed: %s", provider, err)

    if last_err:
        _LOGGER.debug("All providers failed, last error: %s", last_err)

    return None
